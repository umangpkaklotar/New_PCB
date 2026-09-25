// =====================================================
// PCB AI Inspection System
// Upload + Camera Inspection
// Class-wise Defect Grouping
// =====================================================


// =====================================================
// DOM Elements
// =====================================================

const uploadModeBtn =
    document.getElementById("uploadModeBtn");

const cameraModeBtn =
    document.getElementById("cameraModeBtn");

const uploadMode =
    document.getElementById("uploadMode");

const cameraMode =
    document.getElementById("cameraMode");

const pcbFile =
    document.getElementById("pcbFile");

const selectedFile =
    document.getElementById("selectedFile");

const uploadPreview =
    document.getElementById("uploadPreview");

const uploadPreviewContainer =
    document.getElementById(
        "uploadPreviewContainer"
    );

const inspectUploadBtn =
    document.getElementById(
        "inspectUploadBtn"
    );

const cameraVideo =
    document.getElementById("cameraVideo");

const cameraCanvas =
    document.getElementById("cameraCanvas");

const cameraPlaceholder =
    document.getElementById(
        "cameraPlaceholder"
    );

const startCameraBtn =
    document.getElementById(
        "startCameraBtn"
    );

const scanCameraBtn =
    document.getElementById(
        "scanCameraBtn"
    );

const stopCameraBtn =
    document.getElementById(
        "stopCameraBtn"
    );

const resultSection =
    document.getElementById(
        "resultSection"
    );

const resultStatus =
    document.getElementById(
        "resultStatus"
    );

const totalDefects =
    document.getElementById(
        "totalDefects"
    );

const defectList =
    document.getElementById(
        "defectList"
    );

const predictionImage =
    document.getElementById(
        "predictionImage"
    );

const resultProductId =
    document.getElementById(
        "resultProductId"
    );

const productStatus =
    document.getElementById(
        "productStatus"
    );

const resultQRCode =
    document.getElementById(
        "resultQRCode"
    );

const resultMethod =
    document.getElementById(
        "resultMethod"
    );

const resultDate =
    document.getElementById(
        "resultDate"
    );

const barcodeModeBtn =
    document.getElementById(
        "barcodeModeBtn"
    );

const barcodeMode =
    document.getElementById(
        "barcodeMode"
    );

const barcodeError =
    document.getElementById(
        "barcodeError"
    );

// =====================================================
// Global State
// =====================================================

let cameraStream = null;
let html5QrcodeScanner = null;
let currentProductId = null;


// =====================================================
// Upload Mode
// =====================================================

uploadModeBtn.addEventListener(
    "click",
    function () {

        uploadModeBtn.classList.add(
            "active"
        );

        cameraModeBtn.classList.remove(
            "active"
        );
        
        barcodeModeBtn.classList.remove(
            "active"
        );

        uploadMode.classList.add(
            "active-mode"
        );

        cameraMode.classList.remove(
            "active-mode"
        );
        
        barcodeMode.style.display = "none";
        
        stopBarcodeScanner();

    }
);


// =====================================================
// Camera Mode
// =====================================================

cameraModeBtn.addEventListener(
    "click",
    function () {

        cameraModeBtn.classList.add(
            "active"
        );

        uploadModeBtn.classList.remove(
            "active"
        );
        
        barcodeModeBtn.classList.remove(
            "active"
        );

        cameraMode.classList.add(
            "active-mode"
        );

        uploadMode.classList.remove(
            "active-mode"
        );
        
        barcodeMode.style.display = "none";
        
        stopBarcodeScanner();

    }
);


// =====================================================
// Select PCB Image
// =====================================================

pcbFile.addEventListener(
    "change",
    function () {

        const file =
            pcbFile.files[0];

        if (!file) {
            return;
        }

        selectedFile.textContent =
            file.name;

        const imageURL =
            URL.createObjectURL(file);

        uploadPreview.src =
            imageURL;

        uploadPreviewContainer.classList.remove(
            "hidden"
        );

    }
);


// =====================================================
// Upload PCB for Inspection
// =====================================================

inspectUploadBtn.addEventListener(
    "click",
    async function () {

        const file =
            pcbFile.files[0];

        if (!file) {

            alert(
                "Please select a PCB image first."
            );

            return;
        }

        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );
        
        // Generate unique request ID for deduplication
        formData.append(
            "inspection_request_id",
            crypto.randomUUID()
        );
        
        if (currentProductId) {
            formData.append("product_id", currentProductId);
        }

        inspectUploadBtn.disabled =
            true;

        inspectUploadBtn.textContent =
            "Inspecting...";

        try {

            const response =
                await fetch(
                    "/api/inspection/predict",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "PCB inspection failed."
                );

            }

            showInspectionResult(
                data
            );

        } catch (error) {

            console.error(
                "Upload inspection error:",
                error
            );

            alert(
                error.message
            );

        } finally {

            inspectUploadBtn.disabled =
                false;

            inspectUploadBtn.textContent =
                "Inspect PCB";

        }

    }
);


// =====================================================
// Open Camera
// =====================================================

startCameraBtn.addEventListener(
    "click",
    async function () {

        try {

            cameraStream =
                await navigator.mediaDevices.getUserMedia(
                    {
                        video: {
                            facingMode: "environment"
                        },
                        audio: false
                    }
                );

            cameraVideo.srcObject =
                cameraStream;

            cameraPlaceholder.classList.add(
                "hidden"
            );

            startCameraBtn.disabled =
                true;

            scanCameraBtn.disabled =
                false;

            stopCameraBtn.disabled =
                false;

        } catch (error) {

            console.error(
                "Camera error:",
                error
            );

            alert(
                "Camera could not be opened.\n\n" +
                error.message
            );

        }

    }
);


// =====================================================
// Scan PCB From Camera
// =====================================================

scanCameraBtn.addEventListener(
    "click",
    async function () {

        if (!cameraStream) {

            alert(
                "Please open the camera first."
            );

            return;
        }

        const width =
            cameraVideo.videoWidth;

        const height =
            cameraVideo.videoHeight;

        if (
            width === 0 ||
            height === 0
        ) {

            alert(
                "Camera frame is not ready."
            );

            return;
        }

        cameraCanvas.width =
            width;

        cameraCanvas.height =
            height;

        const context =
            cameraCanvas.getContext(
                "2d"
            );

        context.drawImage(
            cameraVideo,
            0,
            0,
            width,
            height
        );

        cameraCanvas.toBlob(
            async function (blob) {

                if (!blob) {

                    alert(
                        "Could not capture camera frame."
                    );

                    return;
                }

                const formData =
                    new FormData();

                formData.append(
                    "file",
                    blob,
                    "camera_pcb.jpg"
                );
                
                // Generate unique request ID for deduplication
                formData.append(
                    "inspection_request_id",
                    crypto.randomUUID()
                );
                
                if (currentProductId) {
                    formData.append("product_id", currentProductId);
                }

                scanCameraBtn.disabled =
                    true;

                scanCameraBtn.textContent =
                    "Scanning...";

                try {

                    const response =
                        await fetch(
                            "/api/inspection/predict",
                            {
                                method: "POST",
                                body: formData
                            }
                        );

                    const data =
                        await response.json();

                    if (!response.ok) {

                        throw new Error(
                            data.detail ||
                            "Camera inspection failed."
                        );

                    }

                    showInspectionResult(
                        data
                    );

                } catch (error) {

                    console.error(
                        "Camera inspection error:",
                        error
                    );

                    alert(
                        error.message
                    );

                } finally {

                    scanCameraBtn.disabled =
                        false;

                    scanCameraBtn.textContent =
                        "Scan PCB";

                }

            },
            "image/jpeg",
            0.95
        );

    }
);


// =====================================================
// Stop Camera
// =====================================================

stopCameraBtn.addEventListener(
    "click",
    function () {

        stopCamera();

    }
);


// =====================================================
// Stop Camera Function
// =====================================================

function stopCamera() {

    if (cameraStream) {

        cameraStream
            .getTracks()
            .forEach(
                function (track) {

                    track.stop();

                }
            );

        cameraStream = null;

    }

    cameraVideo.srcObject =
        null;

    cameraPlaceholder.classList.remove(
        "hidden"
    );

    startCameraBtn.disabled =
        false;

    scanCameraBtn.disabled =
        true;

    stopCameraBtn.disabled =
        true;

}


// =====================================================
// Group Defects By Class
//
// Example:
// mousebite
// mousebite
// spur
// spur
//
// Becomes:
//
// mousebite -> 2
// spur      -> 2
// =====================================================

function groupDefectsByClass(
    defects
) {

    const grouped = {};


    defects.forEach(
        function (defect) {

            const className =
                defect.class_name;


            // -------------------------------------------------
            // Create class entry if it doesn't exist
            // -------------------------------------------------

            if (!grouped[className]) {

                grouped[className] = {

                    count: 0,

                    confidences: []

                };

            }


            // -------------------------------------------------
            // Increase count
            // -------------------------------------------------

            grouped[className].count += 1;


            // -------------------------------------------------
            // Store confidence
            // -------------------------------------------------

            grouped[className]
                .confidences
                .push(
                    defect.confidence
                );

        }
    );


    return grouped;

}


// =====================================================
// Show Inspection Result
// =====================================================

function showInspectionResult(
    data
) {

    // -------------------------------------------------
    // Show result section
    // -------------------------------------------------

    resultSection.classList.remove(
        "hidden"
    );


    // -------------------------------------------------
    // IMPORTANT:
    // Total defects remains actual YOLO detections
    // -------------------------------------------------

    totalDefects.textContent =
        data.total_defects;


    // -------------------------------------------------
    // Show status
    // -------------------------------------------------

    resultStatus.textContent =
        data.status.toUpperCase();

    resultStatus.className =
        "result-status " +
        data.status;


    // -------------------------------------------------
    // Clear old list
    // -------------------------------------------------

    defectList.innerHTML =
        "";


    // -------------------------------------------------
    // No defects
    // -------------------------------------------------

    if (
        data.total_defects === 0
    ) {

        defectList.innerHTML = `

            <div class="defect-item">

                <div class="defect-name">
                    No defects detected
                </div>

                <div class="defect-confidence">
                    PCB appears normal.
                </div>

            </div>

        `;

    }


    // -------------------------------------------------
    // Defects found
    // -------------------------------------------------

    else {

        const groupedDefects =
            groupDefectsByClass(
                data.defects
            );


        // -------------------------------------------------
        // Create one card per defect class
        // -------------------------------------------------

        Object.entries(
            groupedDefects
        ).forEach(
            function (
                [className, info]
            ) {

                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "defect-item";


                // -------------------------------------------------
                // Format confidence values
                // -------------------------------------------------

                const confidenceText =
                    info.confidences
                        .map(
                            function (
                                confidence
                            ) {

                                return (
                                    confidence *
                                    100
                                ).toFixed(1)
                                + "%";

                            }
                        )
                        .join(", ");


                // -------------------------------------------------
                // Display grouped result
                // -------------------------------------------------

                item.innerHTML = `

                    <div class="defect-name">

                        ${className}

                        <span
                            style="
                                margin-left: 8px;
                                background: #2563eb;
                                color: white;
                                padding: 3px 8px;
                                border-radius: 12px;
                                font-size: 12px;
                            "
                        >
                            × ${info.count}
                        </span>

                    </div>


                    <div class="defect-confidence">

                        Confidence:
                        ${confidenceText}

                    </div>

                `;


                defectList.appendChild(
                    item
                );

            }
        );

    }


    // -------------------------------------------------
    // Show prediction image
    // -------------------------------------------------

    if (
        data.prediction_image
    ) {

        predictionImage.src =
            data.prediction_image +
            "?t=" +
            Date.now();

    }


    // -------------------------------------------------
    // Show Product Info
    // -------------------------------------------------

    if (data.product) {
        if (productStatus) {
            productStatus.textContent = data.message;
            if (data.message === "Existing PCB detected") {
                productStatus.style.color = "#3b82f6"; // Blue
            } else {
                productStatus.style.color = "#22c55e"; // Green
            }
        }

        if (resultProductId) {
            resultProductId.textContent = data.product.product_id || "-";
        }
        if (data.product.barcode) {
            try {
                let detailsText = `Product ID: ${data.product.product_id}\n`;
                detailsText += `Barcode: ${data.product.barcode}\n`;
                detailsText += `Method: ${data.inspection_method === "camera" ? "Camera Scan" : "Image Upload"}\n`;
                
                let dateStr = "-";
                if (data.created_at) {
                    dateStr = new Date(data.created_at).toLocaleString();
                }
                detailsText += `Date: ${dateStr}\n`;
                detailsText += `Status: ${data.status}\n`;
                detailsText += `Total Defects: ${data.total_defects}\n`;
                
                if (data.total_defects > 0 && data.defects) {
                    const grouped = groupDefectsByClass(data.defects);
                    Object.entries(grouped).forEach(([className, info]) => {
                        const confs = info.confidences.map(c => (c*100).toFixed(1)+'%').join(', ');
                        detailsText += `${className} x${info.count} (${confs})\n`;
                    });
                }
                
                // Clear previous QR code
                resultQRCode.innerHTML = "";
                
                // Generate new QR code (2D Barcode)
                new QRCode(resultQRCode, {
                    text: detailsText,
                    width: 150,
                    height: 150,
                    colorDark : "#000000",
                    colorLight : "#ffffff",
                    correctLevel : QRCode.CorrectLevel.L
                });
            } catch (e) {
                console.error("QRCode error:", e);
            }
        }
    }

    // -------------------------------------------------
    // Scroll to result
    // -------------------------------------------------

    if (resultMethod && data.inspection_method) {
        resultMethod.textContent = data.inspection_method === "camera" ? "Camera Scan" : "Image Upload";
    } else if (resultMethod) {
        resultMethod.textContent = "-";
    }

    if (resultDate && data.created_at) {
        const date = new Date(data.created_at);
        resultDate.textContent = date.toLocaleString();
    } else if (resultDate) {
        resultDate.textContent = "-";
    }

    resultSection.scrollIntoView({
        behavior: "smooth"
    });

}

// =====================================================
// Barcode Scanner Logic
// =====================================================

barcodeModeBtn.addEventListener("click", () => {
    uploadModeBtn.classList.remove("active");
    cameraModeBtn.classList.remove("active");
    barcodeModeBtn.classList.add("active");
    
    uploadMode.classList.remove("active-mode");
    cameraMode.classList.remove("active-mode");
    
    barcodeMode.style.display = "block";
    uploadMode.style.display = "none";
    cameraMode.style.display = "none";
    resultSection.classList.add("hidden");
    
    startBarcodeScanner();
});

function startBarcodeScanner() {
    if (!html5QrcodeScanner) {
        html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: {width: 250, height: 250} }, false);
        html5QrcodeScanner.render(onScanSuccess, onScanFailure);
    }
}

function stopBarcodeScanner() {
    if (html5QrcodeScanner) {
        html5QrcodeScanner.clear().catch(error => {
            console.error("Failed to clear html5QrcodeScanner. ", error);
        });
        html5QrcodeScanner = null;
    }
}

async function onScanSuccess(decodedText, decodedResult) {
    stopBarcodeScanner();
    
    try {
        // Extract Product ID if the scanned text is our formatted 2D barcode text
        let barcodeId = decodedText;
        const match = decodedText.match(/Product ID:\s*(PCB-\d+)/);
        if (match && match[1]) {
            barcodeId = match[1];
        } else if (decodedText.startsWith("PCB-")) {
            barcodeId = decodedText.trim();
        }
        
        const response = await fetch(`/api/inspection/barcode/${encodeURIComponent(barcodeId)}`);
        
        if (!response.ok) {
            const err = await response.json();
            barcodeError.textContent = err.detail || "PCB not registered";
            barcodeError.style.display = "block";
            // Restart scanner after a delay
            setTimeout(() => {
                barcodeError.style.display = "none";
                startBarcodeScanner();
            }, 3000);
            return;
        }
        
        const data = await response.json();
        
        // Setup data for showInspectionResult
        currentProductId = data.product.barcode;
        
        const mockResultData = {
            product: data.product,
            message: data.message,
            status: data.latest_inspection ? data.latest_inspection.status : "Unknown",
            total_defects: data.latest_inspection ? data.latest_inspection.total_defects : 0,
            defects: data.latest_inspection && data.latest_inspection.defects ? data.latest_inspection.defects : [],
            prediction_image: data.latest_inspection ? data.latest_inspection.prediction_image : "",
            inspection_method: data.latest_inspection ? data.latest_inspection.inspection_method : null,
            created_at: data.latest_inspection ? data.latest_inspection.created_at : null
        };
        
        showInspectionResult(mockResultData);
        resultSection.classList.remove("hidden");
        
    } catch (error) {
        console.error("Scan error:", error);
    }
}

function onScanFailure(error) {
    // handle scan failure, usually better to ignore and keep scanning
}


// =====================================================
// Load Inspection Mode From URL
// =====================================================

function loadInspectionMode() {

    const params =
        new URLSearchParams(
            window.location.search
        );


    const mode =
        params.get("mode");


    if (
        mode === "camera"
    ) {

        cameraModeBtn.click();

    } else {

        uploadModeBtn.click();

    }

}


// =====================================================
// Initial Page Load
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadInspectionMode();

    }
);