"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  askDocument,
  deleteDocument,
  getCurrentUser,
  getJobStatus,
  getResults,
  loginUser,
  listDocuments,
  registerUser,
  submitConsent,
  uploadDocument
} from "./lib/api";
import {
  clearCustomAccessToken,
  getApiAccessToken,
  getAuthProvider,
  isSupabaseAuthEnabled,
  sendSupabasePasswordReset,
  setCustomAccessToken,
  signInWithSupabase,
  signOutSupabase,
  signUpWithSupabase,
  subscribeToSupabaseAuth
} from "./lib/auth";
import { HomeHero } from "./components/home-hero";
import { LexiReminderBanner } from "./components/lexi-reminder-banner";
import { OnboardingModal } from "./components/onboarding-modal";
import { AuthModal } from "./components/auth-modal";
import { UnifiedSidebar } from "./components/unified-sidebar";
import { UnifiedChatInterface } from "./components/unified-chat-interface";
import { PublicHomeView } from "./components/public-home-view";
import { ErrorBanner } from "./components/error-banner";

const ACCEPTED_TYPES = ".pdf,.docx,.png,.jpg,.jpeg";
const AUTH_PROVIDER = getAuthProvider();
const USE_SUPABASE_AUTH = isSupabaseAuthEnabled();

const STATUS_PROGRESS = {
  idle: 0,
  pending: 10,
  uploading: 25,
  extracting_text: 50,
  classifying_document: 70,
  classifying: 70,
  classifying_text: 70,
  extracting_clauses: 88,
  complete: 100,
  failed: 100
};

function prettifyStatus(status) {
  if (!status) {
    return "pending";
  }

  return status.replaceAll("_", " ");
}

function getProgressPercent(status) {
  return STATUS_PROGRESS[status || "idle"] ?? 0;
}

export default function HomePage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentId, setDocumentId] = useState("");
  const [processingConsent, setProcessingConsent] = useState(true);
  const [storageConsent, setStorageConsent] = useState(false);
  const [jobStatus, setJobStatus] = useState("");
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isSubmittingConsent, setIsSubmittingConsent] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [authNotice, setAuthNotice] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [qaThreads, setQaThreads] = useState({});
  const [question, setQuestion] = useState("");
  const [userContext, setUserContext] = useState("");
  const [isAsking, setIsAsking] = useState(false);

  const activeDocument = useMemo(
    () => documents.find((document) => document.document_id === documentId) || null,
    [documents, documentId]
  );
  const activeStatus = activeDocument?.job_status || jobStatus || "idle";
  const activeQaMessages = useMemo(() => qaThreads[documentId] || [], [qaThreads, documentId]);
  const canUpload = useMemo(() => Boolean(selectedFile) && !isUploading, [selectedFile, isUploading]);
  const progressPercent = useMemo(() => getProgressPercent(activeStatus), [activeStatus]);

  useEffect(() => {
    let unsubscribe = () => {};

    const loadUser = async () => {
      try {
        const token = await getApiAccessToken();
        if (!token) {
          resetAuthenticatedSession();
          return;
        }

        await loadAuthenticatedWorkspace();
      } catch {
        if (!USE_SUPABASE_AUTH) {
          clearCustomAccessToken();
        }
        resetAuthenticatedSession();
      } finally {
        setIsAuthLoading(false);
      }
    };

    loadUser();

    if (USE_SUPABASE_AUTH) {
      unsubscribe = subscribeToSupabaseAuth((event, session) => {
        if (event === "SIGNED_OUT" || !session) {
          resetAuthenticatedSession();
        }
      });
    }

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!documentId || !isPolling) {
      return undefined;
    }

    const poll = async () => {
      try {
        const statusData = await getJobStatus(documentId);
        setJobStatus(statusData.status);

        if (statusData.status === "complete") {
          const data = await getResults(documentId);
          setResults(data);
          setIsPolling(false);
          await loadDocumentHistory(documentId);
        }

        if (statusData.status === "failed") {
          setError(statusData.error_message || "Processing failed. Please try again.");
          setIsPolling(false);
          await loadDocumentHistory(documentId);
        }
      } catch (pollError) {
        setError(pollError.message);
        setIsPolling(false);
      }
    };

    poll();
    const timer = setInterval(poll, 2500);

    return () => clearInterval(timer);
  }, [documentId, isPolling]);

  function resetAuthenticatedSession() {
    setCurrentUser(null);
    setDocumentId("");
    setResults(null);
    setJobStatus("");
    setDocuments([]);
    setQaThreads({});
    setQuestion("");
    setUserContext("");
    setIsPolling(false);
  }

  async function loadAuthenticatedWorkspace() {
    const user = await getCurrentUser();
    setCurrentUser(user);

    const history = await loadDocumentHistory();
    if (history.length > 0) {
      await handleSelectDocument(history[0].document_id, history[0]);
    }

    return user;
  }

  async function loadDocumentHistory(preferredDocumentId = "") {
    setIsLoadingDocuments(true);

    try {
      const payload = await listDocuments();
      const nextDocuments = payload.documents || [];
      setDocuments(nextDocuments);

      if (preferredDocumentId && !nextDocuments.some((document) => document.document_id === preferredDocumentId)) {
        setDocumentId("");
      }

      return nextDocuments;
    } catch (historyError) {
      setError(historyError.message);
      return [];
    } finally {
      setIsLoadingDocuments(false);
    }
  }

  async function handleSelectDocument(nextDocumentId, knownDocument = null) {
    if (!nextDocumentId) {
      return;
    }

    setDocumentId(nextDocumentId);
    setSelectedFile(null);
    setQuestion("");
    setUserContext("");
    setError("");
    setResults(null);
    setIsPolling(false);

    try {
      let nextStatus = knownDocument?.job_status || "";
      try {
        const statusData = await getJobStatus(nextDocumentId);
        nextStatus = statusData.status;
      } catch {
        // A newly uploaded document can be awaiting consent and have no job record yet.
      }

      setJobStatus(nextStatus || "");

      if (nextStatus === "complete") {
        const data = await getResults(nextDocumentId);
        setResults(data);
        return;
      }

      if (nextStatus && nextStatus !== "failed") {
        setIsPolling(true);
      }
    } catch (selectError) {
      setError(selectError.message);
    }
  }

  function startNewUpload() {
    setSelectedFile(null);
    setDocumentId("");
    setJobStatus("");
    setResults(null);
    setQuestion("");
    setUserContext("");
    setError("");
    setIsPolling(false);
    setProcessingConsent(true);
    setStorageConsent(false);
  }

  function resetFlow() {
    setSelectedFile(null);
    setDocumentId("");
    setJobStatus("");
    setResults(null);
    setError("");
    setIsPolling(false);
    setIsUploading(false);
    setIsSubmittingConsent(false);
    setQuestion("");
    setUserContext("");
    setProcessingConsent(true);
    setStorageConsent(false);
  }

  function pickFile(file) {
    if (!file) {
      return;
    }

    setSelectedFile(file);
    setDocumentId("");
    setJobStatus("");
    setResults(null);
    setQuestion("");
    setUserContext("");
    setIsPolling(false);
    setError("");
    setProcessingConsent(true);
    setStorageConsent(false);
  }

  function onFileInputChange(event) {
    pickFile(event.target.files?.[0]);
  }

  function onDrop(event) {
    event.preventDefault();
    setIsDragging(false);
    pickFile(event.dataTransfer.files?.[0]);
  }

  async function handleUpload() {
    if (!selectedFile) {
      setError("Select a file first.");
      return;
    }

    setIsUploading(true);
    setError("");
    setResults(null);
    setJobStatus("uploading");

    try {
      const uploaded = await uploadDocument(selectedFile);
      setDocumentId(uploaded.document_id);
      setJobStatus("pending");
      await loadDocumentHistory(uploaded.document_id);
    } catch (uploadError) {
      setError(uploadError.message);
      setJobStatus("");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setIsAuthenticating(true);
    setError("");
    setAuthNotice("");

    try {
      if (USE_SUPABASE_AUTH) {
        if (authMode === "register") {
          const signUpResult = await signUpWithSupabase(email, password);

          if (!signUpResult.session) {
            setAuthNotice("Check your email to confirm your account, then log in.");
            setAuthMode("login");
            setPassword("");
            return;
          }
        } else {
          const signInResult = await signInWithSupabase(email, password);
          if (!signInResult.session) {
            throw new Error("Supabase did not return a session. Check your email verification status.");
          }
        }

        await loadAuthenticatedWorkspace();
      } else {
        if (authMode === "register") {
          await registerUser(email, password);
        }

        const loginResult = await loginUser(email, password);
        setCustomAccessToken(loginResult.access_token);

        await loadAuthenticatedWorkspace();
      }

      setPassword("");
      setShowAuthModal(false);
    } catch (authError) {
      setError(authError.message);
    } finally {
      setIsAuthenticating(false);
    }
  }

  async function handleLogout() {
    setError("");

    try {
      if (USE_SUPABASE_AUTH) {
        await signOutSupabase();
      } else {
        clearCustomAccessToken();
      }
    } catch (logoutError) {
      setError(logoutError.message);
    } finally {
      resetAuthenticatedSession();
    }
  }

  async function handleConsentSubmit(event) {
    event.preventDefault();

    if (!documentId) {
      setError("Upload a document first.");
      return;
    }

    setIsSubmittingConsent(true);
    setError("");

    try {
      await submitConsent(documentId, processingConsent, storageConsent);

      if (!processingConsent) {
        resetFlow();
        await loadDocumentHistory();
        return;
      }

      setIsPolling(true);
      setJobStatus("extracting_text");
      await loadDocumentHistory(documentId);
    } catch (consentError) {
      setError(consentError.message);
    } finally {
      setIsSubmittingConsent(false);
    }
  }

  async function handleDelete() {
    if (!documentId) {
      setError("No document is active.");
      return;
    }

    setIsDeleting(true);
    setError("");

    try {
      await deleteDocument(documentId);
      resetFlow();
      const remainingDocuments = await loadDocumentHistory();
      if (remainingDocuments.length > 0) {
        await handleSelectDocument(remainingDocuments[0].document_id, remainingDocuments[0]);
      }
    } catch (deleteError) {
      setError(deleteError.message);
    } finally {
      setIsDeleting(false);
    }
  }

  function handleExportPdf() {
    if (!results) {
      return;
    }

    window.print();
  }

  function appendQaMessage(targetDocumentId, message) {
    setQaThreads((currentThreads) => ({
      ...currentThreads,
      [targetDocumentId]: [...(currentThreads[targetDocumentId] || []), message]
    }));
  }

  async function handleAsk() {
    const trimmedQuestion = question.trim();
    const trimmedContext = userContext.trim();

    if (!documentId || !results) {
      setError("Choose a processed document before asking a question.");
      return;
    }

    if (!trimmedQuestion) {
      return;
    }

    setIsAsking(true);
    setError("");
    setQuestion("");

    appendQaMessage(documentId, {
      id: `${Date.now()}-user`,
      role: "user",
      question: trimmedQuestion,
      userContext: trimmedContext
    });

    try {
      const answer = await askDocument(documentId, trimmedQuestion, trimmedContext);
      appendQaMessage(documentId, {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        answer: answer.answer,
        citations: answer.citations || [],
        isAnswered: answer.is_answered,
        userContextNote: answer.user_context_note
      });
    } catch (askError) {
      appendQaMessage(documentId, {
        id: `${Date.now()}-assistant-error`,
        role: "assistant",
        answer: askError.message,
        citations: [],
        isAnswered: false
      });
    } finally {
      setIsAsking(false);
    }
  }

  function openAuthModal() {
    setAuthMode("login");
    setAuthNotice("");
    setShowAuthModal(true);
  }

  function handleAuthModeChange(nextMode) {
    setAuthMode(nextMode);
    setAuthNotice("");
  }

  async function handlePasswordReset() {
    const trimmedEmail = email.trim();

    if (!trimmedEmail) {
      setError("Enter your email before requesting a password reset.");
      return;
    }

    setIsAuthenticating(true);
    setError("");
    setAuthNotice("");

    try {
      await sendSupabasePasswordReset(trimmedEmail);
      setAuthNotice("Password reset email sent if this account exists.");
    } catch (resetError) {
      setError(resetError.message);
    } finally {
      setIsAuthenticating(false);
    }
  }

  return (
    <main className="shell">
      <HomeHero
        showPublicActions={!currentUser && !isAuthLoading}
        onStartDocument={openAuthModal}
      />
      <LexiReminderBanner />

      {!currentUser && !isAuthLoading && <PublicHomeView onStartDocument={openAuthModal} />}

      <section className="workspace" id="document-workspace" aria-label="Document workspace">
        <div className="workspace-shell">
          {currentUser && (
            <aside className="workspace-sidebar">
              <UnifiedSidebar
                currentUser={currentUser}
                onLogout={handleLogout}
                activeDocumentId={documentId}
                documents={documents}
                isLoadingDocuments={isLoadingDocuments}
                onSelectDocument={handleSelectDocument}
                onStartNewUpload={startNewUpload}
              />
            </aside>
          )}

          <div className="workspace-main" style={currentUser ? {} : { gridColumn: "1 / -1" }}>
            {currentUser ? (
              <UnifiedChatInterface
                acceptedTypes={ACCEPTED_TYPES}
                canUpload={canUpload}
                isDragging={isDragging}
                isUploading={isUploading}
                onDrop={onDrop}
                onDragOver={(event) => {
                  event.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onFileInputChange={onFileInputChange}
                onUpload={handleUpload}
                selectedFile={selectedFile}
                documentId={documentId}
                isSubmittingConsent={isSubmittingConsent}
                onConsentSubmit={handleConsentSubmit}
                processingConsent={processingConsent}
                setProcessingConsent={setProcessingConsent}
                setStorageConsent={setStorageConsent}
                storageConsent={storageConsent}
                activeDocument={activeDocument}
                isDeleting={isDeleting}
                isPolling={isPolling}
                jobStatus={jobStatus}
                onDelete={handleDelete}
                onStartNewUpload={startNewUpload}
                prettifyStatus={prettifyStatus}
                progressPercent={progressPercent}
                results={results}
                onExportPdf={handleExportPdf}
                isAsking={isAsking}
                messages={activeQaMessages}
                onAsk={handleAsk}
                question={question}
                setQuestion={setQuestion}
                setUserContext={setUserContext}
                userContext={userContext}
              />
            ) : null}
          </div>
        </div>
      </section>

      <AnimatePresence>
        {error ? (
          <ErrorBanner error={error} onDismiss={() => setError("")} />
        ) : null}
      </AnimatePresence>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        authMode={authMode}
        onAuthModeChange={handleAuthModeChange}
        authNotice={authNotice}
        authProvider={AUTH_PROVIDER}
        email={email}
        onEmailChange={setEmail}
        password={password}
        onPasswordChange={setPassword}
        onPasswordReset={handlePasswordReset}
        onSubmit={handleAuthSubmit}
        isAuthenticating={isAuthenticating}
      />

      <OnboardingModal disabled={showAuthModal} />
    </main>
  );
}
