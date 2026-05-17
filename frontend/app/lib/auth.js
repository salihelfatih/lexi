import { createClient } from "@supabase/supabase-js";

const CUSTOM_ACCESS_TOKEN_KEY = "lexi_access_token";
const AUTH_PROVIDER = (process.env.NEXT_PUBLIC_AUTH_PROVIDER || "custom").toLowerCase();

let supabaseClient;

function hasBrowserStorage() {
  return typeof window !== "undefined" && window.localStorage;
}

function getSupabaseClient() {
  if (supabaseClient) {
    return supabaseClient;
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    throw new Error("Supabase auth is enabled, but Supabase frontend settings are missing.");
  }

  supabaseClient = createClient(supabaseUrl, supabaseKey);
  return supabaseClient;
}

function requireSupabaseAuth() {
  if (!isSupabaseAuthEnabled()) {
    throw new Error("Supabase auth is not enabled for this frontend build.");
  }

  return getSupabaseClient();
}

function throwSupabaseError(error) {
  if (error) {
    throw new Error(error.message || "Supabase authentication failed.");
  }
}

export function getAuthProvider() {
  return AUTH_PROVIDER;
}

export function isSupabaseAuthEnabled() {
  return AUTH_PROVIDER === "supabase";
}

export async function getApiAccessToken() {
  if (isSupabaseAuthEnabled()) {
    const supabase = requireSupabaseAuth();
    const { data, error } = await supabase.auth.getSession();
    throwSupabaseError(error);
    return data.session?.access_token || "";
  }

  if (!hasBrowserStorage()) {
    return "";
  }

  return window.localStorage.getItem(CUSTOM_ACCESS_TOKEN_KEY) || "";
}

export function setCustomAccessToken(token) {
  if (hasBrowserStorage()) {
    window.localStorage.setItem(CUSTOM_ACCESS_TOKEN_KEY, token);
  }
}

export function clearCustomAccessToken() {
  if (hasBrowserStorage()) {
    window.localStorage.removeItem(CUSTOM_ACCESS_TOKEN_KEY);
  }
}

export async function signUpWithSupabase(email, password) {
  const supabase = requireSupabaseAuth();
  const { data, error } = await supabase.auth.signUp({ email, password });
  throwSupabaseError(error);
  return data;
}

export async function signInWithSupabase(email, password) {
  const supabase = requireSupabaseAuth();
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  throwSupabaseError(error);
  return data;
}

export async function signOutSupabase() {
  const supabase = requireSupabaseAuth();
  const { error } = await supabase.auth.signOut();
  throwSupabaseError(error);
}

export function subscribeToSupabaseAuth(callback) {
  if (!isSupabaseAuthEnabled()) {
    return () => {};
  }

  const supabase = requireSupabaseAuth();
  const { data } = supabase.auth.onAuthStateChange(callback);
  return () => data.subscription.unsubscribe();
}

export async function sendSupabasePasswordReset(email) {
  const supabase = requireSupabaseAuth();
  const redirectTo = typeof window !== "undefined" ? window.location.origin : undefined;
  const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo });
  throwSupabaseError(error);
}
