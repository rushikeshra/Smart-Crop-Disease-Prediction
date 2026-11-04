// Smart Crop AI - Main JavaScript Utilities

document.addEventListener("DOMContentLoaded", function () {
    // Auto-dismiss alert messages after 6 seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {}
        }, 6000);
    });

    // File Upload Drag & Drop and Preview Handler
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    const uploadPlaceholder = document.getElementById("uploadPlaceholder");
    const previewContainer = document.getElementById("previewContainer");
    const imagePreview = document.getElementById("imagePreview");
    const submitUploadBtn = document.getElementById("submitUploadBtn");
    const removeUploadBtn = document.getElementById("removeUploadBtn");
    const uploadForm = document.getElementById("uploadForm");
    const loadingOverlay = document.getElementById("loadingOverlay");

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", function (e) {
            if (e.target !== removeUploadBtn && !removeUploadBtn?.contains(e.target)) {
                fileInput.click();
            }
        });

        // Drag & Drop visual feedback
        ["dragenter", "dragover"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("dragover");
            }, false);
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("dragover");
            }, false);
        });

        // Handle Dropped Files
        dropzone.addEventListener("drop", (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        // Handle File Input Selection
        fileInput.addEventListener("change", function () {
            if (this.files && this.files[0]) {
                handleFileSelect(this.files[0]);
            }
        });

        function handleFileSelect(file) {
            // Validate file size (16MB max)
            if (file.size > 16 * 1024 * 1024) {
                alert("File size exceeds 16MB limit. Please choose a smaller image.");
                resetUpload();
                return;
            }

            const validTypes = ["image/jpeg", "image/jpg", "image/png"];
            if (!validTypes.includes(file.type.toLowerCase())) {
                alert("Invalid file format. Please upload JPG or PNG images.");
                resetUpload();
                return;
            }

            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                uploadPlaceholder.classList.add("d-none");
                previewContainer.classList.remove("d-none");
                if (submitUploadBtn) submitUploadBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }

        function resetUpload() {
            fileInput.value = "";
            imagePreview.src = "#";
            uploadPlaceholder.classList.remove("d-none");
            previewContainer.classList.add("d-none");
            if (submitUploadBtn) submitUploadBtn.disabled = true;
        }

        if (removeUploadBtn) {
            removeUploadBtn.addEventListener("click", function (e) {
                e.stopPropagation();
                resetUpload();
            });
        }
    }

    // Submit Loading Overlay Trigger
    if (uploadForm) {
        uploadForm.addEventListener("submit", function () {
            if (submitUploadBtn) {
                submitUploadBtn.disabled = true;
                submitUploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Running Inference...';
            }
        });
    }

    // ==========================================================
    // LIVE CAMERA CAPTURE CONTROLS
    // ==========================================================
    const tabUploadBtn = document.getElementById("tab-upload-btn");
    const tabCameraBtn = document.getElementById("tab-camera-btn");
    const cameraVideo = document.getElementById("cameraVideo");
    const cameraCanvas = document.getElementById("cameraCanvas");
    const cameraLiveView = document.getElementById("cameraLiveView");
    const cameraCapturedView = document.getElementById("cameraCapturedView");
    const cameraPreviewImg = document.getElementById("cameraPreviewImg");
    const snapPhotoBtn = document.getElementById("snapPhotoBtn");
    const retakePhotoBtn = document.getElementById("retakePhotoBtn");
    const switchCameraBtn = document.getElementById("switchCameraBtn");
    const startCameraBtn = document.getElementById("startCameraBtn");
    const cameraAlert = document.getElementById("cameraAlert");
    const cameraBase64Input = document.getElementById("cameraBase64Input");
    const submitBtnText = document.getElementById("submitBtnText");

    let cameraStream = null;
    let currentFacingMode = "environment"; // default to rear camera for scanning foliage

    function showCameraAlert(message, isWarning = true) {
        if (!cameraAlert) return;
        cameraAlert.innerHTML = `<i class="fa-solid fa-triangle-exclamation me-1"></i> ${message}`;
        cameraAlert.className = `alert ${isWarning ? "alert-warning" : "alert-danger"} py-2 px-3 small mt-3 text-start mb-0`;
        cameraAlert.classList.remove("d-none");
    }

    function hideCameraAlert() {
        if (cameraAlert) cameraAlert.classList.add("d-none");
    }

    async function startCamera() {
        hideCameraAlert();
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showCameraAlert("Live camera access is not supported by your browser or environment. Please use the Upload Photo File tab instead.");
            if (snapPhotoBtn) snapPhotoBtn.classList.add("d-none");
            if (startCameraBtn) startCameraBtn.classList.remove("d-none");
            return;
        }

        try {
            stopCamera();
            const constraints = {
                video: {
                    facingMode: currentFacingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };

            cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
            if (cameraVideo) {
                cameraVideo.srcObject = cameraStream;
                await cameraVideo.play();
            }
            if (startCameraBtn) startCameraBtn.classList.add("d-none");
            if (snapPhotoBtn) snapPhotoBtn.classList.remove("d-none");
            if (cameraLiveView) cameraLiveView.classList.remove("d-none");
            if (cameraCapturedView) cameraCapturedView.classList.add("d-none");
        } catch (err) {
            console.warn("Primary camera constraint failed, attempting fallback:", err);
            // Try generic fallback without facingMode constraints
            try {
                cameraStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
                if (cameraVideo) {
                    cameraVideo.srcObject = cameraStream;
                    await cameraVideo.play();
                }
                if (startCameraBtn) startCameraBtn.classList.add("d-none");
                if (snapPhotoBtn) snapPhotoBtn.classList.remove("d-none");
                if (cameraLiveView) cameraLiveView.classList.remove("d-none");
                if (cameraCapturedView) cameraCapturedView.classList.add("d-none");
            } catch (fallbackErr) {
                console.error("Camera access failed:", fallbackErr);
                showCameraAlert("Camera access was blocked or is unavailable. Please grant camera permission in your browser or switch to the Upload File tab.", true);
                if (startCameraBtn) startCameraBtn.classList.remove("d-none");
                if (snapPhotoBtn) snapPhotoBtn.classList.add("d-none");
            }
        }
    }

    function stopCamera() {
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            cameraStream = null;
        }
        if (cameraVideo) {
            cameraVideo.srcObject = null;
        }
    }

    function snapPhoto() {
        if (!cameraVideo || !cameraCanvas) return;
        const width = cameraVideo.videoWidth || 640;
        const height = cameraVideo.videoHeight || 480;

        cameraCanvas.width = width;
        cameraCanvas.height = height;
        const ctx = cameraCanvas.getContext("2d");
        ctx.drawImage(cameraVideo, 0, 0, width, height);

        const dataUrl = cameraCanvas.toDataURL("image/jpeg", 0.92);

        // Store into hidden form input for submission
        if (cameraBase64Input) {
            cameraBase64Input.value = dataUrl;
        }

        // Preview captured frame
        if (cameraPreviewImg) {
            cameraPreviewImg.src = dataUrl;
        }
        if (cameraLiveView) cameraLiveView.classList.add("d-none");
        if (cameraCapturedView) cameraCapturedView.classList.remove("d-none");
        if (snapPhotoBtn) snapPhotoBtn.classList.add("d-none");
        if (retakePhotoBtn) retakePhotoBtn.classList.remove("d-none");

        // Enable submission
        if (submitUploadBtn) submitUploadBtn.disabled = false;
        if (submitBtnText) submitBtnText.textContent = "Run AI Diagnosis on Captured Leaf";

        // Stop camera stream to conserve battery
        stopCamera();
    }

    function retakePhoto() {
        if (cameraBase64Input) cameraBase64Input.value = "";
        if (cameraCapturedView) cameraCapturedView.classList.add("d-none");
        if (cameraLiveView) cameraLiveView.classList.remove("d-none");
        if (retakePhotoBtn) retakePhotoBtn.classList.add("d-none");
        if (snapPhotoBtn) snapPhotoBtn.classList.remove("d-none");
        if (submitUploadBtn) submitUploadBtn.disabled = true;

        startCamera();
    }

    // Camera button event bindings
    if (snapPhotoBtn) snapPhotoBtn.addEventListener("click", snapPhoto);
    if (retakePhotoBtn) retakePhotoBtn.addEventListener("click", retakePhoto);
    if (startCameraBtn) startCameraBtn.addEventListener("click", startCamera);

    if (switchCameraBtn) {
        switchCameraBtn.addEventListener("click", function () {
            currentFacingMode = (currentFacingMode === "environment") ? "user" : "environment";
            startCamera();
        });
    }

    // Tab Switch Actions
    if (tabCameraBtn) {
        tabCameraBtn.addEventListener("shown.bs.tab", function () {
            if (submitBtnText) submitBtnText.textContent = "Run AI Diagnosis on Captured Leaf";
            if (cameraBase64Input && cameraBase64Input.value) {
                // Photo already snapped
                if (submitUploadBtn) submitUploadBtn.disabled = false;
            } else {
                if (submitUploadBtn) submitUploadBtn.disabled = true;
                startCamera();
            }
        });
    }

    if (tabUploadBtn) {
        tabUploadBtn.addEventListener("shown.bs.tab", function () {
            stopCamera();
            if (submitBtnText) submitBtnText.textContent = "Run AI Diagnosis on Uploaded Leaf";
            // Check if file is selected in upload tab
            if (fileInput && fileInput.files && fileInput.files.length > 0) {
                if (submitUploadBtn) submitUploadBtn.disabled = false;
            } else {
                if (submitUploadBtn) submitUploadBtn.disabled = true;
            }
        });
    }

    // Clean up camera when user navigates away
    window.addEventListener("beforeunload", stopCamera);
});
