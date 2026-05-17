const ERROR_MESSAGES = [
  {
    match: /failed to fetch|networkerror|load failed/i,
    message: "Lexi could not reach the backend. Check that the API is running and try again."
  },
  {
    match: /invalid email or password|unauthorized|not authenticated|401/i,
    message: "Please check your email and password, then try again."
  },
  {
    match: /email already registered|409/i,
    message: "An account already exists for that email. Try logging in instead."
  },
  {
    match: /file size exceeds|413/i,
    message: "That file is too large for Lexi to process right now."
  },
  {
    match: /unsupported file format|unsupported media|415/i,
    message: "Lexi currently accepts PDF, DOCX, JPEG, and PNG files."
  },
  {
    match: /job status not found|job not found|access denied|404/i,
    message: "Lexi could not find that document in your workspace anymore."
  },
  {
    match: /supabase.*missing|supabase auth is not configured/i,
    message: "Supabase auth settings are missing for this frontend build."
  }
];

export function getUserFriendlyError(error) {
  if (!error) {
    return "";
  }

  const rawMessage = typeof error === "string" ? error : error.message;
  const message = rawMessage?.trim();

  if (!message) {
    return "Something went wrong. Please try again.";
  }

  const friendlyMatch = ERROR_MESSAGES.find(({ match }) => match.test(message));
  if (friendlyMatch) {
    return friendlyMatch.message;
  }

  return message;
}
