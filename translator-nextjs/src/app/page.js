"use client";

import { useState, useEffect } from "react";
import Modal from "@/components/Modal";
import Analytics from "@/components/Analytics";
import BatchHistory from "@/components/BatchHistory";

// Normalize API base URL so we don't accidentally end up with `/api/api/...`
const rawApiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7860";
// Remove trailing slashes and a trailing `/api` segment if present
const API_BASE_URL = rawApiBase.replace(/\/+$/, "").replace(/\/api$/, "");

// Optional default Gemini key from environment. If the user leaves the API key
// field empty *and* service === 'gemini', we'll fall back to this.
const DEFAULT_GEMINI_API_KEY =
  process.env.NEXT_PUBLIC_DEFAULT_GEMINI_API_KEY || "";

// Ensure errors coming from the backend are safe to render in React.
const formatError = (err) => {
  if (!err) return "";
  if (typeof err === "string") return err;
  try {
    return JSON.stringify(err);
  } catch {
    return String(err);
  }
};

export default function Home() {
  const [authenticated, setAuthenticated] = useState(false);
  const [sessionState, setSessionState] = useState("");
  const [loading, setLoading] = useState(false);
  const [inputMethod, setInputMethod] = useState("manual");
  const [driveLink, setDriveLink] = useState("");
  const [folders, setFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState("");
  const [files, setFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [language, setLanguage] = useState("Spanish");
  const [service, setService] = useState("gemini"); // 'gemini' or 'openrouter'
  const [model, setModel] = useState("gemini-2.5-pro");
  const [apiKey, setApiKey] = useState("");
  const [translating, setTranslating] = useState(false);
  const [progress, setProgress] = useState(null);
  const [batchProgress, setBatchProgress] = useState(null); // Individual file batch progress
  const [results, setResults] = useState([]);
  const [uploadModal, setUploadModal] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [folderNameInput, setFolderNameInput] = useState("");
  const [manualFiles, setManualFiles] = useState([]);

  // Load saved settings from localStorage on mount (excluding API key for security)
  useEffect(() => {
    const savedService = localStorage.getItem("translator_service");
    const savedModel = localStorage.getItem("translator_model");
    const savedLanguage = localStorage.getItem("translator_language");
    const savedInputMethod = localStorage.getItem("translator_input_method");

    if (savedService) setService(savedService);
    if (savedModel) setModel(savedModel);
    if (savedLanguage) setLanguage(savedLanguage);
    if (savedInputMethod) setInputMethod(savedInputMethod);
  }, []);

  useEffect(() => {
    localStorage.setItem("translator_service", service);
  }, [service]);

  useEffect(() => {
    localStorage.setItem("translator_model", model);
  }, [model]);

  useEffect(() => {
    localStorage.setItem("translator_language", language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem("translator_input_method", inputMethod);
  }, [inputMethod]);

  // Update model when service changes (only if not loading from localStorage)
  useEffect(() => {
    const savedModel = localStorage.getItem("translator_model");
    if (!savedModel) {
      if (service === "gemini") {
        setModel("gemini-2.5-flash");
      } else {
        setModel("anthropic/claude-3.5-sonnet");
      }
    }
  }, [service]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);

    // Check if this is a popup callback window
    if (params.get("authenticated") === "true" && window.opener) {
      const state = params.get("state");
      console.log("Popup detected auth callback with state:", state);
      console.log("window.opener exists:", !!window.opener);
      console.log("Sending message to origin:", window.location.origin);

      if (state) {
        // Send message to parent window
        try {
          window.opener.postMessage(
            {
              type: "GOOGLE_AUTH_SUCCESS",
              state: state,
            },
            window.location.origin
          );
          console.log("Message sent successfully");
        } catch (error) {
          console.error("Error sending message:", error);
        }

        // Show success message and close popup
        document.body.innerHTML = `
          <div style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: system-ui, -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div style="text-align: center; background: white; padding: 3rem; border-radius: 1rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
              <div style="font-size: 4rem; margin-bottom: 1rem;">✅</div>
              <h1 style="color: #10b981; margin-bottom: 0.5rem;">Authentication Successful!</h1>
              <p style="color: #6b7280;">Returning to app...</p>
              <p style="color: #9ca3af; font-size: 0.875rem; margin-top: 1rem;">This window will close automatically in 2 seconds</p>
            </div>
          </div>
        `;
        setTimeout(() => {
          console.log("Closing popup window");
          window.close();
        }, 2000);
      }
      return;
    }

    // Handle auth error in popup
    if (params.get("error") && window.opener) {
      window.opener.postMessage(
        {
          type: "GOOGLE_AUTH_ERROR",
          error: params.get("error"),
        },
        window.location.origin
      );

      document.body.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: system-ui, -apple-system, sans-serif; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <div style="text-align: center; background: white; padding: 3rem; border-radius: 1rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">❌</div>
            <h1 style="color: #ef4444; margin-bottom: 0.5rem;">Authentication Failed</h1>
            <p style="color: #6b7280;">Please try again.</p>
            <p style="color: #9ca3af; font-size: 0.875rem; margin-top: 1rem;">Closing automatically in 3 seconds...</p>
          </div>
        </div>
      `;
      setTimeout(() => window.close(), 3000);
      return;
    }

    // Listen for messages from popup window
    const handleMessage = (event) => {
      console.log(
        "Received message:",
        event.data,
        "from origin:",
        event.origin
      );

      // Verify origin for security
      if (event.origin !== window.location.origin) {
        console.log("Message rejected - origin mismatch");
        return;
      }

      if (event.data.type === "GOOGLE_AUTH_SUCCESS") {
        console.log("Auth success, setting state:", event.data.state);

        // Clear timeout if it exists
        if (window._authTimeout) {
          clearTimeout(window._authTimeout);
          window._authTimeout = null;
        }

        setSessionState(event.data.state);
        setAuthenticated(true);
        localStorage.setItem("drive_session_state", event.data.state);
        setLoading(false);
      } else if (event.data.type === "GOOGLE_AUTH_ERROR") {
        console.log("Auth error:", event.data.error);

        // Clear timeout if it exists
        if (window._authTimeout) {
          clearTimeout(window._authTimeout);
          window._authTimeout = null;
        }

        setLoading(false);
      }
    };

    window.addEventListener("message", handleMessage);

    // Check if we have a saved session state
    const savedState = localStorage.getItem("drive_session_state");
    if (savedState) {
      // Validate the session with the backend before setting as authenticated
      validateSession(savedState);
    }

    return () => {
      window.removeEventListener("message", handleMessage);
    };
  }, []);

  // Validate session with backend
  const validateSession = async (state) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/drive/folders?state=${state}`
      );
      if (response.ok) {
        // Session is valid
        setSessionState(state);
        setAuthenticated(true);
      } else {
        // Session is invalid, clear it
        console.log("Session validation failed, clearing localStorage");
        localStorage.removeItem("drive_session_state");
        setAuthenticated(false);
        setSessionState("");
      }
    } catch (error) {
      // Backend not reachable or session invalid
      console.error("Failed to validate session:", error);
      localStorage.removeItem("drive_session_state");
      setAuthenticated(false);
      setSessionState("");
    }
  };

  const handleConnect = async () => {
    setLoading(true);
    try {
      console.log("API_BASE_URL", API_BASE_URL);
      const response = await fetch(`${API_BASE_URL}/api/drive/auth`);
      console.log("response", response);

      const data = await response.json();

      if (data.authUrl) {
        // Open OAuth in a popup window
        const width = 600;
        const height = 700;
        const left = window.screen.width / 2 - width / 2;
        const top = window.screen.height / 2 - height / 2;

        const popup = window.open(
          data.authUrl,
          "Google OAuth",
          `width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no,scrollbars=yes,resizable=yes`
        );

        if (!popup) {
          alert("Please allow popups for this site to connect to Google Drive");
          setLoading(false);
        } else {
          // Set a timeout to stop loading state if nothing happens
          const timeout = setTimeout(() => {
            setLoading(false);
            console.log("Auth timeout - checking localStorage as fallback");

            // Check if auth succeeded via localStorage
            const newState = localStorage.getItem("drive_session_state");
            if (newState && newState !== sessionState) {
              console.log("Found new session state in localStorage");
              setSessionState(newState);
              setAuthenticated(true);
            }
          }, 60000); // 60 second timeout

          // Store timeout ID to clear it if auth succeeds earlier
          window._authTimeout = timeout;
        }
      }
    } catch (error) {
      console.error("Failed to connect to Google Drive:", error);
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/drive/logout?state=${sessionState}`, {
        method: "POST",
      });
      setAuthenticated(false);
      setSessionState("");
      localStorage.removeItem("drive_session_state");
      setFolders([]);
      setFiles([]);
      setSelectedFiles([]);
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const loadFolders = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/drive/folders?state=${sessionState}`
      );
      const data = await response.json();

      if (data.error || data.detail) {
        alert(data.error || data.detail);
        return;
      }

      setFolders(data.folders || []);
    } catch (error) {
      alert("Failed to load folders");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadFilesFromLink = async () => {
    if (!driveLink.trim()) {
      alert("Please enter a Google Drive link");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/drive/files?state=${sessionState}&driveLink=${encodeURIComponent(
          driveLink
        )}`
      );
      const data = await response.json();

      if (data.error || data.detail) {
        alert(data.error || data.detail);
        return;
      }

      if (data.type === "file") {
        setFiles([data.file]);
      } else {
        setFiles(data.files || []);
      }
    } catch (error) {
      alert("Failed to load files from link");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadFilesFromFolder = async (folderId) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/drive/files?state=${sessionState}&folderId=${folderId}`
      );
      const data = await response.json();

      if (data.error || data.detail) {
        alert(data.error || data.detail);
        return;
      }

      setFiles(data.files || []);
    } catch (error) {
      alert("Failed to load files");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleFolderChange = (folderId) => {
    setSelectedFolder(folderId);
    if (folderId) {
      loadFilesFromFolder(folderId);
    } else {
      setFiles([]);
    }
  };

  const handleFileSelect = (fileId) => {
    setSelectedFiles((prev) => {
      if (prev.includes(fileId)) {
        return prev.filter((id) => id !== fileId);
      } else {
        return [...prev, fileId];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedFiles.length === files.length) {
      setSelectedFiles([]);
    } else {
      setSelectedFiles(files.map((f) => f.id));
    }
  };

  const handleManualFileUpload = async (event) => {
    const uploadedFiles = Array.from(event.target.files);

    // Filter for DOCX files only
    const docxFiles = uploadedFiles.filter(
      (file) =>
        file.type ===
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
        file.name.endsWith(".docx")
    );

    if (docxFiles.length === 0) {
      alert("Please upload only DOCX files");
      return;
    }

    if (docxFiles.length !== uploadedFiles.length) {
      console.log(
        `${uploadedFiles.length - docxFiles.length} non-DOCX file(s) ignored`
      );
    }

    setLoading(true);

    try {
      // Convert files to base64 and store them
      const processedFiles = await Promise.all(
        docxFiles.map(async (file) => {
          const base64Data = await fileToBase64(file);
          return {
            id: `manual-${Date.now()}-${Math.random()
              .toString(36)
              .substr(2, 9)}`,
            name: file.name,
            size: file.size,
            mimeType:
              "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            base64Data: base64Data,
            isManual: true,
          };
        })
      );

      setManualFiles(processedFiles);
      setFiles(processedFiles);
      console.log(`${processedFiles.length} file(s) uploaded successfully`);
    } catch (error) {
      alert("Failed to upload files: " + error.message);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        // Remove the data URL prefix to get just the base64 string
        const base64String = reader.result.split(",")[1];
        resolve(base64String);
      };
      reader.onerror = (error) => reject(error);
    });
  };

  const handleRemoveManualFile = (fileId) => {
    setManualFiles((prev) => prev.filter((f) => f.id !== fileId));
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
    setSelectedFiles((prev) => prev.filter((id) => id !== fileId));
  };

  // Poll for batch progress for individual file
  const pollBatchProgress = (progressId, onError) => {
    let pollCount = 0;
    let lastCompletedBatches = -1; // Track last completed batches count
    let lastProgressTime = Date.now(); // Track when we last saw progress
    const STUCK_TIMEOUT = 10 * 60 * 1000; // 10 minutes without progress = stuck
    const startTime = Date.now();

    const intervalId = setInterval(async () => {
      pollCount++;

      // Check if stuck (no progress for 10 minutes)
      const timeSinceProgress = Date.now() - lastProgressTime;
      if (timeSinceProgress > STUCK_TIMEOUT) {
        const totalElapsed = Date.now() - startTime;
        console.error(
          `🔴 [STUCK] No progress for ${Math.round(timeSinceProgress / 1000)}s (total: ${Math.round(totalElapsed / 1000)}s)`
        );
        clearInterval(intervalId);
        if (onError) {
          onError(
            `Translation appears stuck - no progress for ${Math.round(
              timeSinceProgress / 1000
            )} seconds. Last completed: ${lastCompletedBatches} batches.`
          );
        }
        return;
      }

      // Log every 10 polls to avoid spam
      if (pollCount % 10 === 0) {
        const totalElapsed = Date.now() - startTime;
        const timeSinceProgress = Date.now() - lastProgressTime;
        console.log(
          `🔵 [POLLING] Poll #${pollCount}, total: ${Math.round(totalElapsed / 1000)}s, no progress: ${Math.round(timeSinceProgress / 1000)}s`
        );
      }

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/translate/progress/${progressId}`
        );
        if (response.ok) {
          const data = await response.json();

          // Check if progress was made
          if (data.completedBatches !== lastCompletedBatches) {
            // Progress made! Reset the stuck timer
            lastProgressTime = Date.now();
            console.log(
              `🔵 [PROGRESS] ${data.completedBatches}/${data.totalBatches} batches complete`
            );
          } else if (pollCount % 10 === 0) {
            // No progress, but log every 10 polls
            console.log(
              `🔵 [WAITING] ${data.completedBatches}/${data.totalBatches} batches complete (waiting...)`
            );
          }
          lastCompletedBatches = data.completedBatches;

          // Check if there's an error flag from backend
          if (data.error) {
            console.error(
              "🔴 [BACKEND ERROR] Backend reported error during translation"
            );
            clearInterval(intervalId);
            if (onError) {
              onError("Translation failed during batch processing");
            }
            return;
          }

          setBatchProgress({
            completedBatches: data.completedBatches,
            totalBatches: data.totalBatches,
            error: data.error || false,
          });

          // Auto-stop if all batches are complete
          if (
            data.totalBatches > 0 &&
            data.completedBatches >= data.totalBatches
          ) {
            console.log("✅ [COMPLETE] All batches complete, stopping polling");
            clearInterval(intervalId);
            return;
          }

          // Note: The translation completion will also clear the interval as a backup
        } else if (response.status === 404) {
          // Progress ID not found - translation may have failed
          console.warn("Progress ID not found - translation may have failed");
          clearInterval(intervalId);
          if (onError) {
            onError(
              "Translation progress not found. The translation may have failed."
            );
          }
        }
      } catch (error) {
        console.error("Failed to fetch batch progress:", error);
        // Don't stop on network errors, but log them
        if (pollCount > 10) {
          // After 10 failed attempts, give up
          clearInterval(intervalId);
          if (onError) {
            onError("Failed to check translation progress. Network error.");
          }
        }
      }
    }, 1000); // Poll every 1 second

    return intervalId;
  };

  const handleTranslate = async () => {
    // Allow a default Gemini key from env when the input field is empty.
    const effectiveApiKey =
      apiKey || (service === "gemini" ? DEFAULT_GEMINI_API_KEY : "");

    if (!effectiveApiKey) {
      alert(
        `Please enter your ${
          service === "gemini" ? "Gemini" : "OpenRouter"
        } API key`
      );
      return;
    }

    if (selectedFiles.length === 0) {
      alert("Please select at least one file");
      return;
    }

    console.log(`🔵 [START] Translation process initiated`);
    console.log(`   Files to translate: ${selectedFiles.length}`);
    console.log(`   Service: ${service}, Model: ${model}`);
    console.log(`   Target language: ${language}`);

    setTranslating(true);
    setProgress({ current: 0, total: selectedFiles.length });
    setBatchProgress(null);
    setResults([]);

    const newResults = [];
    console.log(`🔵 [INIT] Starting file processing loop...`);
    let pollingInterval = null;

    for (let i = 0; i < selectedFiles.length; i++) {
      const fileId = selectedFiles[i];
      const file = files.find((f) => f.id === fileId);

      if (!file) continue;

      console.log(`\n${"=".repeat(80)}`);
      console.log(
        `🔵 [FILE ${i + 1}/${selectedFiles.length}] Processing: ${file.name}`
      );
      console.log(`${"=".repeat(80)}`);

      // Update file-level progress - show current file being processed, but don't increment completed count yet
      setProgress({
        current: newResults.length, // Number of files completed so far
        total: selectedFiles.length,
        fileName: file.name,
      });

      // Generate unique progress ID for this file
      const progressId = `translate-${Date.now()}-${Math.random()
        .toString(36)
        .substr(2, 9)}`;

      console.log(`🔵 [PROGRESS ID] Generated: ${progressId}`);

      // Reset batch progress for new file
      setBatchProgress({ completedBatches: 0, totalBatches: 0 });

      // Clear any existing polling interval
      if (pollingInterval) {
        console.log(`🔵 [CLEANUP] Clearing previous polling interval`);
        clearInterval(pollingInterval);
      }

      // Flag to track if polling detected an error
      let pollingErrorDetected = false;
      let pollingErrorMessage = "";

      // Start polling for batch progress with error callback
      console.log(`🔵 [POLLING] Starting progress polling for ${file.name}`);
      pollingInterval = pollBatchProgress(progressId, (errorMsg) => {
        pollingErrorDetected = true;
        pollingErrorMessage = errorMsg;
        // Update UI to show error state
        setBatchProgress((prev) => ({
          ...prev,
          error: true,
        }));
        // Log error
        console.error(
          `🔴 [POLLING ERROR] Translation failed for ${file.name}:`,
          errorMsg
        );
      });

      try {
        let fileData;

        // Check if this is a manually uploaded file or a Drive file
        if (file.isManual) {
          // Use the stored base64 data
          fileData = file.base64Data;
        } else {
          // Download from Google Drive
          const downloadResponse = await fetch(
            `${API_BASE_URL}/api/drive/download?state=${sessionState}&fileId=${fileId}&mimeType=${encodeURIComponent(
              file.mimeType
            )}`
          );
          const downloadData = await downloadResponse.json();

          if (downloadData.error || downloadData.detail) {
            newResults.push({
              fileName: file.name,
              success: false,
              error: formatError(downloadData.error || downloadData.detail),
            });
            // Clear polling for failed download
            if (pollingInterval) clearInterval(pollingInterval);
            setBatchProgress(null);
            continue;
          }

          fileData = downloadData.data;
        }

        // Translate file - use correct endpoint based on service
        const translateEndpoint =
          service === "openrouter"
            ? `${API_BASE_URL}/api/translate/openrouter`
            : `${API_BASE_URL}/api/translate`;

        let translateData;
        try {
          console.log(`🔵 [STEP 1] Starting translation for: ${file.name}`);
          console.log(`   Endpoint: ${translateEndpoint}`);
          console.log(`   Language: ${language}, Model: ${model}`);

          // No timeout on fetch - polling will detect if stuck
          console.log(`   No fetch timeout - polling will detect if stuck (10min no progress)`);

          console.log(`🔵 [STEP 2] Sending translation request to backend...`);
          const translateResponse = await fetch(translateEndpoint, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              fileData: fileData,
              fileName: file.name,
              language,
              model,
              // Backend expects "apiKey" field; always send the effective key
              apiKey: effectiveApiKey,
              progressId, // Include progress ID for polling
            }),
          });
          console.log(
            `🔵 [STEP 3] Received response from backend (status: ${translateResponse.status})`
          );

          if (!translateResponse.ok) {
            console.log(
              `🔴 [ERROR] Backend returned error status: ${translateResponse.status}`
            );
            throw new Error(
              `Translation request failed: ${translateResponse.status} ${translateResponse.statusText}`
            );
          }

          console.log(`🔵 [STEP 4] Parsing response JSON...`);
          translateData = await translateResponse.json();
          console.log(`🔵 [STEP 5] Translation complete! Received data:`, {
            hasDocument: !!translateData.translatedDocument,
            hasLogs: !!translateData.logs,
            hasError: !!translateData.error,
            logCount: translateData.logs?.length || 0,
          });
        } catch (error) {
          console.log(`🔴 [ERROR] Translation request failed:`, error);
          console.log(`   Error name: ${error.name}`);
          console.log(`   Error message: ${error.message}`);

          // Stop polling on any error
          if (pollingInterval) {
            console.log(`🔵 [CLEANUP] Stopping polling interval`);
            clearInterval(pollingInterval);
            pollingInterval = null;
          }
          setBatchProgress(null);

          newResults.push({
            fileName: file.name,
            success: false,
            error: error.message || "Translation request failed",
          });
          await new Promise((resolve) => setTimeout(resolve, 500));
          continue;
        } finally {
          // Always stop polling after fetch completes (success or error)
          if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
          }
        }

        // Check if polling detected an error during translation
        if (pollingErrorDetected) {
          newResults.push({
            fileName: file.name,
            success: false,
            error:
              pollingErrorMessage ||
              "Translation failed during batch processing",
          });
          setBatchProgress(null);
          await new Promise((resolve) => setTimeout(resolve, 500));
          continue;
        }

        if (translateData.error || translateData.detail) {
          newResults.push({
            fileName: file.name,
            success: false,
            error: formatError(translateData.error || translateData.detail),
          });
          setBatchProgress(null);
          await new Promise((resolve) => setTimeout(resolve, 500));
          continue;
        }

        // Success
        const baseName = file.name.replace(/\.[^/.]+$/, "");
        const translatedFileName = `${baseName}_${language.toLowerCase()}_translated.docx`;

        // Log batch sizes to browser console
        console.log(`\n📊 Translation Complete: ${file.name}`);
        console.log("─".repeat(60));
        if (translateData.logs) {
          // Filter and display batch size information
          const batchSizeLogs = translateData.logs.filter(
            (log) =>
              log.includes("[BATCH SIZE]") ||
              log.includes("[SMART BATCHING]") ||
              log.includes("[EFFICIENCY]") ||
              log.includes("[CONTENT ANALYSIS]")
          );
          batchSizeLogs.forEach((log) => console.log(log));

          // Also log all logs for debugging
          console.log("\n📝 Full Translation Logs:");
          translateData.logs.forEach((log) => console.log(log));
        }
        console.log("─".repeat(60) + "\n");

        newResults.push({
          fileName: file.name,
          translatedFileName,
          success: true,
          data: translateData.translatedDocument,
          logs: translateData.logs,
          stats: translateData.stats,
        });

        // Show completion state with all batches complete
        setBatchProgress({
          completedBatches: batchProgress?.totalBatches || 1,
          totalBatches: batchProgress?.totalBatches || 1,
        });

        // Update progress to reflect this file is now complete
        setProgress({
          current: newResults.length,
          total: selectedFiles.length,
          fileName: file.name,
          completed: true, // Flag to show completion state
        });

        // Add a small delay so user can see the completion before moving to next file
        await new Promise((resolve) => setTimeout(resolve, 800));

        // Clear batch progress after delay
        setBatchProgress(null);
      } catch (error) {
        // Clear polling on error
        if (pollingInterval) {
          clearInterval(pollingInterval);
          pollingInterval = null;
        }
        setBatchProgress(null);

        newResults.push({
          fileName: file.name,
          success: false,
          error: error.message,
        });

        // Add delay after error too
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    }

    // Ensure polling is stopped
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }

    setResults(newResults);
    setTranslating(false);
    setProgress(null);
    setBatchProgress(null);

    const successCount = newResults.filter((r) => r.success).length;
    console.log(
      `Translation complete! ${successCount} of ${newResults.length} files successful`
    );
  };

  const handleDownload = (result) => {
    const byteCharacters = atob(result.data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = result.translatedFileName;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleDownloadAll = () => {
    const successfulResults = results.filter((r) => r.success);
    successfulResults.forEach((result, idx) => {
      setTimeout(() => handleDownload(result), idx * 200);
    });
    console.log(`Downloading ${successfulResults.length} files...`);
  };

  const handleUploadToDrive = async (result, targetFolderId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/drive/upload`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          state: sessionState,
          folderId: targetFolderId,
          fileName: result.translatedFileName,
          fileData: result.data,
          mimeType:
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }),
      });

      const data = await response.json();

      if (data.error || data.detail) {
        alert(`Upload failed: ${data.error || data.detail}`);
        return null;
      }

      return data;
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
      console.error(error);
      return null;
    }
  };

  const openUploadModal = () => {
    if (!sessionState) {
      alert("Please connect to Google Drive first");
      return;
    }
    const defaultName = `Translated_${language}_${
      new Date().toISOString().split("T")[0]
    }`;
    setFolderNameInput(defaultName);
    setUploadModal(true);
  };

  const confirmUpload = async () => {
    if (!folderNameInput.trim()) {
      alert("Please enter a folder name");
      return;
    }

    setUploadProgress({ current: 0, total: 0, status: "Creating folder..." });

    try {
      const createFolderResponse = await fetch(
        `${API_BASE_URL}/api/drive/create-folder`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            state: sessionState,
            folderName: folderNameInput,
          }),
        }
      );

      const folderData = await createFolderResponse.json();

      if (folderData.error || folderData.detail) {
        alert(
          `Failed to create folder: ${folderData.error || folderData.detail}`
        );
        setUploadProgress(null);
        return;
      }

      const folderId = folderData.folderId;
      const folderLink = folderData.webViewLink;

      const successfulResults = results.filter((r) => r.success);
      setUploadProgress({
        current: 0,
        total: successfulResults.length,
        status: "Uploading files...",
      });

      let uploadedCount = 0;

      for (let i = 0; i < successfulResults.length; i++) {
        const result = successfulResults[i];
        setUploadProgress({
          current: i + 1,
          total: successfulResults.length,
          status: `Uploading ${result.translatedFileName}...`,
        });

        const uploadResult = await handleUploadToDrive(result, folderId);

        if (uploadResult && uploadResult.success !== false) {
          uploadedCount++;
        }
      }

      setUploadProgress(null);
      setUploadModal(false);

      if (uploadedCount > 0) {
        console.log(
          `✅ Uploaded ${uploadedCount} files to Drive successfully!`
        );

        if (folderLink) {
          setTimeout(() => {
            if (
              confirm(
                `Would you like to open the folder in Google Drive?\n\n${folderLink}`
              )
            ) {
              window.open(folderLink, "_blank");
            }
          }, 500);
        }
      } else {
        alert("No files were uploaded successfully");
      }
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
      console.error(error);
      setUploadProgress(null);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Upload Modal */}
        <Modal
          isOpen={uploadModal}
          onClose={() => setUploadModal(false)}
          title="☁️ Upload to Google Drive"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Create a new folder and upload all translated files to your Google
              Drive.
            </p>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Folder Name
              </label>
              <input
                type="text"
                value={folderNameInput}
                onChange={(e) => setFolderNameInput(e.target.value)}
                className="w-full p-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter folder name..."
              />
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>{results.filter((r) => r.success).length} files</strong>{" "}
                will be uploaded to this folder
              </p>
            </div>

            {uploadProgress && (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">{uploadProgress.status}</p>
                <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-blue-600 h-full transition-all duration-300"
                    style={{
                      width: `${
                        (uploadProgress.current / uploadProgress.total) * 100
                      }%`,
                    }}
                  />
                </div>
                <p className="text-xs text-gray-500 text-center">
                  {uploadProgress.current} of {uploadProgress.total}
                </p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setUploadModal(false)}
                disabled={uploadProgress !== null}
                className="flex-1 px-4 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Cancel
              </button>
              <button
                onClick={confirmUpload}
                disabled={uploadProgress !== null}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition"
              >
                {uploadProgress ? "Uploading..." : "Upload"}
              </button>
            </div>
          </div>
        </Modal>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-6xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-3">
            Document Translator
          </h1>
          <p className="text-gray-600 text-lg">
            🚀 Batch Translation • 📊 Real-time Analytics • ☁️ Drive Integration
            • 📤 Manual Upload
          </p>
        </div>

        {/* API Key Section - STEP 1 */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 mb-6 border border-gray-200">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span className="text-2xl">🔑</span>
            Step 1: API Configuration
          </h2>

          {/* Service Selector */}
          <div className="mb-4">
            <label className="block text-sm font-bold text-gray-700 mb-2">
              AI Service Provider
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setService("gemini")}
                className={`py-3 px-4 rounded-xl font-semibold transition transform ${
                  service === "gemini"
                    ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                🤖 Google Gemini
              </button>
              <button
                onClick={() => setService("openrouter")}
                className={`py-3 px-4 rounded-xl font-semibold transition transform ${
                  service === "openrouter"
                    ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg scale-105"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                🌐 OpenRouter
              </button>
            </div>
          </div>

          {/* API Key Input */}
          <div className="relative">
            <input
              type="password"
              className="w-full p-4 pr-24 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
              placeholder={
                service === "gemini"
                  ? "Enter your Gemini API key..."
                  : "Enter your OpenRouter API key..."
              }
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            {apiKey && (
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
                <button
                  onClick={() => {
                    setApiKey("");
                  }}
                  className="text-red-500 hover:text-red-700 text-sm px-2 py-1 rounded"
                  title="Clear API key"
                >
                  🗑️
                </button>
                <span className="text-green-500 text-xl">✓</span>
              </div>
            )}
          </div>
          {apiKey ? (
            <p className="mt-2 text-sm text-green-600 flex items-center gap-1">
              <span>🔒</span> API key stored securely in memory only (will be
              cleared on page refresh)
            </p>
          ) : (
            <p className="mt-2 text-sm text-gray-500">
              Get your API key from{" "}
              {service === "gemini" ? (
                <a
                  href="https://aistudio.google.com/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline font-semibold"
                >
                  Google AI Studio
                </a>
              ) : (
                <a
                  href="https://openrouter.ai/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-purple-600 hover:underline font-semibold"
                >
                  OpenRouter Dashboard
                </a>
              )}
            </p>
          )}
        </div>

        {/* Input Method Selection - STEP 2 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">
            📂 Step 2: Choose Input Method
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <button
              onClick={() => {
                setInputMethod("manual");
                // Clear Drive files when switching to manual
                setFiles([]);
                setSelectedFiles([]);
                setSelectedFolder("");
                setDriveLink("");
              }}
              className={`py-4 px-4 rounded-lg font-semibold transition ${
                inputMethod === "manual"
                  ? "bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              <div className="text-2xl mb-2">📤</div>
              Upload DOCX Files
            </button>
            <button
              onClick={() => {
                setInputMethod("link");
                // Clear manual files when switching to Drive
                setManualFiles([]);
                setFiles([]);
                setSelectedFiles([]);
                if (!authenticated) {
                  alert("Please connect to Google Drive first");
                }
              }}
              className={`py-4 px-4 rounded-lg font-semibold transition ${
                inputMethod === "link"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              <div className="text-2xl mb-2">🔗</div>
              Google Drive Link
            </button>
            <button
              onClick={() => {
                setInputMethod("browse");
                // Clear manual files when switching to Drive
                setManualFiles([]);
                setFiles([]);
                setSelectedFiles([]);
                if (!authenticated) {
                  alert("Please connect to Google Drive first");
                } else if (folders.length === 0) {
                  loadFolders();
                }
              }}
              className={`py-4 px-4 rounded-lg font-semibold transition ${
                inputMethod === "browse"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              <div className="text-2xl mb-2">📁</div>
              Browse Drive Folders
            </button>
          </div>

          {/* Manual Upload UI */}
          {inputMethod === "manual" && (
            <div>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={handleManualFileUpload}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-6xl mb-4">📄</div>
                  <p className="text-lg font-semibold text-gray-700 mb-2">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-sm text-gray-500">
                    DOCX files only • Multiple files supported
                  </p>
                </label>
              </div>
              {loading && (
                <div className="mt-4 text-center">
                  <p className="text-gray-600">Processing files...</p>
                </div>
              )}
            </div>
          )}

          {/* Google Drive Connection - Show only when needed */}
          {(inputMethod === "link" || inputMethod === "browse") &&
            !authenticated && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-blue-900 mb-2">
                  🔗 Connect to Google Drive
                </h3>
                <p className="mb-2 text-blue-800 text-sm">
                  To use Google Drive features, please connect your account.
                  This is a secure OAuth process.
                </p>
                <p className="mb-4 text-blue-700 text-xs flex items-center gap-1">
                  <span>🪟</span> Authentication will open in a popup window -
                  you won&apos;t lose your current work
                </p>
                <button
                  onClick={handleConnect}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
                >
                  {loading ? "Opening popup..." : "🔗 Connect to Google Drive"}
                </button>
              </div>
            )}

          {authenticated &&
            (inputMethod === "link" || inputMethod === "browse") && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4 flex items-center justify-between">
                <span className="text-green-700 font-semibold text-sm">
                  ✅ Connected to Google Drive
                </span>
                <button
                  onClick={handleDisconnect}
                  className="bg-red-500 text-white py-1 px-3 rounded text-sm hover:bg-red-600 transition"
                >
                  Disconnect
                </button>
              </div>
            )}

          {/* Google Drive Link Input */}
          {inputMethod === "link" && authenticated && (
            <div>
              <div className="flex gap-2">
                <input
                  type="text"
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://drive.google.com/drive/folders/... or file link"
                  value={driveLink}
                  onChange={(e) => setDriveLink(e.target.value)}
                />
                <button
                  onClick={loadFilesFromLink}
                  disabled={loading}
                  className="bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition"
                >
                  {loading ? "Loading..." : "Load Files"}
                </button>
              </div>
            </div>
          )}

          {/* Browse Drive Folders */}
          {inputMethod === "browse" && authenticated && (
            <div>
              <select
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={selectedFolder}
                onChange={(e) => handleFolderChange(e.target.value)}
                disabled={loading}
              >
                <option value="">Select a folder...</option>
                {folders.map((folder) => (
                  <option key={folder.id} value={folder.id}>
                    📁 {folder.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* File Selection */}
        {files.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">📄 Step 3: Select Files</h2>
              <button
                onClick={handleSelectAll}
                className="text-blue-600 hover:text-blue-800 font-semibold"
              >
                {selectedFiles.length === files.length
                  ? "☑️ Deselect All"
                  : "✅ Select All"}
              </button>
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {files.map((file) => {
                const mimeTypeLabels = {
                  "application/vnd.google-apps.document": "Google Doc",
                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    "Word Doc",
                  "application/pdf": "PDF",
                };
                const typeLabel = mimeTypeLabels[file.mimeType] || "Document";
                const fileSize = file.size
                  ? ` (${(file.size / 1024).toFixed(1)} KB)`
                  : "";

                return (
                  <div
                    key={file.id}
                    className={`p-4 border-2 rounded-lg transition ${
                      selectedFiles.includes(file.id)
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div
                        className="flex items-center gap-3 flex-1 cursor-pointer"
                        onClick={() => handleFileSelect(file.id)}
                      >
                        <input
                          type="checkbox"
                          checked={selectedFiles.includes(file.id)}
                          onChange={() => {}}
                          className="w-5 h-5"
                        />
                        <div>
                          <p className="font-semibold">{file.name}</p>
                          <p className="text-sm text-gray-500">
                            {typeLabel}
                            {fileSize}
                          </p>
                        </div>
                      </div>
                      {file.isManual && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRemoveManualFile(file.id);
                          }}
                          className="ml-2 text-red-600 hover:text-red-800 font-semibold text-sm"
                          title="Remove file"
                        >
                          ❌
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            <p className="mt-4 text-sm text-gray-600">
              Selected {selectedFiles.length} of {files.length} file(s)
            </p>
          </div>
        )}

        {/* Translation Settings */}
        {selectedFiles.length > 0 && (
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 mb-6 border border-gray-200">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <span className="text-2xl">⚙️</span>
              Step 4: Translation Settings
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Target Language
                </label>
                <select
                  className="w-full p-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                >
                  <option>Contemporary English</option>
                  <option>Spanish</option>
                  <option>German</option>
                  <option>Dutch</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  {service === "gemini"
                    ? "🤖 Gemini Model"
                    : "🌐 OpenRouter Model"}
                </label>
                <select
                  className="w-full p-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                >
                  {service === "gemini" ? (
                    <>
                      <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                      <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                    </>
                  ) : (
                    <>
                      <option value="anthropic/claude-sonnet-4">
                        Claude 4 Sonnet
                      </option>
                      <option value="openai/gpt-5">GPT-5</option>
                      <option value="google/gemini-2.5-pro">
                        Gemini 2.5 Pro
                      </option>
                    </>
                  )}
                </select>
              </div>
            </div>

            <button
              onClick={handleTranslate}
              disabled={
                translating ||
                (!apiKey && service === "gemini" && !DEFAULT_GEMINI_API_KEY)
              }
              className="w-full mt-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-lg font-bold text-lg hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition"
            >
              {translating
                ? `🔄 Translating... (${progress?.current || 0}/${
                    progress?.total || 0
                  } completed)`
                : `🚀 Start Translation (${selectedFiles.length} file${
                    selectedFiles.length > 1 ? "s" : ""
                  })`}
            </button>

            {progress && (
              <div className="mt-4 space-y-4">
                {/* File-level progress */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-semibold text-gray-700">
                      📁 Overall Progress
                    </span>
                    <span className="text-sm font-bold text-blue-600">
                      {progress.current} / {progress.total} files completed
                    </span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-blue-600 h-full transition-all duration-300"
                      style={{
                        width: `${(progress.current / progress.total) * 100}%`,
                      }}
                    />
                  </div>
                  <p className="text-sm text-gray-600 mt-2 text-center">
                    {progress.fileName &&
                      (progress.completed
                        ? `✅ Completed: ${progress.fileName}`
                        : `⏳ Currently processing: ${progress.fileName}`)}
                  </p>
                </div>

                {/* Batch-level progress (within current file) */}
                {batchProgress && batchProgress.totalBatches > 0 && (
                  <div
                    className={`rounded-lg p-4 border transition-all duration-300 ${
                      batchProgress.error
                        ? "bg-red-50 border-red-200"
                        : batchProgress.completedBatches ===
                          batchProgress.totalBatches
                        ? "bg-green-50 border-green-200"
                        : "bg-blue-50 border-blue-200"
                    }`}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span
                        className={`text-sm font-semibold ${
                          batchProgress.error
                            ? "text-red-800"
                            : batchProgress.completedBatches ===
                              batchProgress.totalBatches
                            ? "text-green-800"
                            : "text-blue-800"
                        }`}
                      >
                        📊 Current File Batches
                      </span>
                      <span
                        className={`text-sm font-bold ${
                          batchProgress.error
                            ? "text-red-600"
                            : batchProgress.completedBatches ===
                              batchProgress.totalBatches
                            ? "text-green-600"
                            : "text-blue-600"
                        }`}
                      >
                        {batchProgress.completedBatches} /{" "}
                        {batchProgress.totalBatches} batches
                      </span>
                    </div>
                    <div
                      className={`rounded-full h-3 overflow-hidden ${
                        batchProgress.error
                          ? "bg-red-200"
                          : batchProgress.completedBatches ===
                            batchProgress.totalBatches
                          ? "bg-green-200"
                          : "bg-blue-200"
                      }`}
                    >
                      <div
                        className={`h-full transition-all duration-300 ${
                          batchProgress.error
                            ? "bg-gradient-to-r from-red-500 to-red-600"
                            : batchProgress.completedBatches ===
                              batchProgress.totalBatches
                            ? "bg-gradient-to-r from-green-500 to-emerald-600"
                            : "bg-gradient-to-r from-indigo-500 to-purple-600"
                        }`}
                        style={{
                          width: `${
                            (batchProgress.completedBatches /
                              batchProgress.totalBatches) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                    <p
                      className={`text-xs mt-2 text-center ${
                        batchProgress.error
                          ? "text-red-700 font-semibold"
                          : batchProgress.completedBatches ===
                            batchProgress.totalBatches
                          ? "text-green-700 font-semibold"
                          : "text-blue-700"
                      }`}
                    >
                      {batchProgress.error
                        ? "❌ Translation failed! Skipping to next file..."
                        : batchProgress.completedBatches ===
                          batchProgress.totalBatches
                        ? "✅ All batches completed!"
                        : `⏳ Processing batch ${
                            batchProgress.completedBatches + 1
                          }...`}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">📊 Translation Results</h2>
              {results.some((r) => r.success) && (
                <div className="flex gap-2">
                  <button
                    onClick={handleDownloadAll}
                    className="bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition flex items-center gap-2"
                  >
                    📥 Download All
                  </button>
                  <button
                    onClick={openUploadModal}
                    disabled={loading}
                    className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition flex items-center gap-2 disabled:bg-gray-400"
                    title="Create a new folder in Drive and upload all translated files"
                  >
                    ☁️ Upload to Drive
                  </button>
                </div>
              )}
            </div>

            {results.some((r) => r.success) && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
                💡 <strong>Tip:</strong> Use &ldquo;Upload to Drive&rdquo; to
                save all translated files directly to your Google Drive in a new
                folder.
              </div>
            )}

            <div className="space-y-4">
              {results.map((result, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-2 ${
                    result.success
                      ? "border-green-200 bg-green-50"
                      : "border-red-200 bg-red-50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-semibold">
                        {result.success ? "✅" : "❌"} {result.fileName}
                      </p>
                      {result.success ? (
                        <div className="mt-2 text-sm text-gray-600">
                          <p>Paragraphs: {result.stats?.paragraphCount || 0}</p>
                          <p>
                            Total Tokens:{" "}
                            {result.stats?.totalTokens?.toLocaleString() || 0}
                          </p>
                        </div>
                      ) : (
                        <p className="mt-1 text-sm text-red-600">
                          Error: {result.error}
                        </p>
                      )}
                    </div>
                    {result.success && (
                      <button
                        onClick={() => handleDownload(result)}
                        className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition ml-4"
                      >
                        📥 Download
                      </button>
                    )}
                  </div>

                  {/* Analytics Dashboard */}
                  {result.success && result.stats && (
                    <div className="mt-6">
                      <Analytics stats={result.stats} />
                    </div>
                  )}

                  {/* Translated Content Preview */}
                  {result.success && result.stats?.translatedText && (
                    <div className="mt-6">
                      <h4 className="font-semibold text-gray-700 mb-2">
                        📖 Translated Content Preview
                      </h4>
                      <div className="bg-white rounded-lg border border-gray-300 p-4 max-h-96 overflow-y-auto">
                        <pre className="whitespace-pre-wrap text-sm font-sans text-gray-800">
                          {result.stats.translatedText}
                        </pre>
                      </div>
                      <p className="mt-2 text-xs text-gray-500">
                        💬{" "}
                        {result.stats.translatedText
                          .split(" ")
                          .filter((w) => w)
                          .length.toLocaleString()}{" "}
                        words • 📄 {result.stats.paragraphCount} paragraphs
                      </p>
                    </div>
                  )}

                  {result.success && result.logs && (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800 font-medium">
                        🔍 View Processing Logs
                      </summary>
                      <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-x-auto max-h-48 overflow-y-auto">
                        {result.logs.join("\n")}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
