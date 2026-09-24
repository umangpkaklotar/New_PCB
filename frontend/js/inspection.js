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


// =====================================================
// Camera Stream
// =====================================================

let cameraStream = null;


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

        uploadMode.classList.add(
            "active-mode"
        );

        cameraMode.classList.remove(
            "active-mode"
        );

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

        cameraMode.classList.add(
            "active-mode"
        );

        uploadMode.classList.remove(
            "active-mode"
        );

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
    // Save dashboard statistics
    // -------------------------------------------------

    saveInspectionStatistics(
        data
    );


    // -------------------------------------------------
    // Scroll to result
    // -------------------------------------------------

    resultSection.scrollIntoView({
        behavior: "smooth"
    });

}


// =====================================================
// Save Dashboard Statistics
// =====================================================

function saveInspectionStatistics(
    data
) {

    let totalInspections =
        Number(
            localStorage.getItem(
                "pcb_total_inspections"
            )
        ) || 0;


    let defectiveInspections =
        Number(
            localStorage.getItem(
                "pcb_defective_inspections"
            )
        ) || 0;


    let normalInspections =
        Number(
            localStorage.getItem(
                "pcb_normal_inspections"
            )
        ) || 0;


    let totalDefects =
        Number(
            localStorage.getItem(
                "pcb_total_defects"
            )
        ) || 0;


    // -------------------------------------------------
    // Add one inspection
    // -------------------------------------------------

    totalInspections += 1;


    // -------------------------------------------------
    // Defective / Normal
    // -------------------------------------------------

    if (
        data.status === "defective"
    ) {

        defectiveInspections += 1;

    } else {

        normalInspections += 1;

    }


    // -------------------------------------------------
    // Add all actual YOLO detections
    // -------------------------------------------------

    totalDefects +=
        Number(
            data.total_defects
        ) || 0;


    // -------------------------------------------------
    // Save
    // -------------------------------------------------

    localStorage.setItem(
        "pcb_total_inspections",
        totalInspections
    );


    localStorage.setItem(
        "pcb_defective_inspections",
        defectiveInspections
    );


    localStorage.setItem(
        "pcb_normal_inspections",
        normalInspections
    );


    localStorage.setItem(
        "pcb_total_defects",
        totalDefects
    );


    // -------------------------------------------------
    // Debug
    // -------------------------------------------------

    console.log(
        "Dashboard statistics updated:",
        {
            totalInspections,
            defectiveInspections,
            normalInspections,
            totalDefects
        }
    );

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