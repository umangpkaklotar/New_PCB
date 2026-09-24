// =====================================================
// PCB AI Inspection System
// Dashboard Statistics
// =====================================================


// =====================================================
// Get Stored Statistics
// =====================================================

async function getInspectionStats() {

    try {
        const response = await fetch('/api/dashboard/stats');
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error("Failed to fetch stats from API", error);
    }

    return {
        totalInspections: 0,
        defectivePcb: 0,
        normalPcb: 0,
        totalDefects: 0
    };

}


// =====================================================
// Display Statistics on Dashboard
// =====================================================

async function displayDashboardStats() {

    const stats = await getInspectionStats();


    // -------------------------------------------------
    // Total Inspections
    // -------------------------------------------------

    const totalElement =
        document.getElementById(
            "totalInspections"
        );


    if (totalElement) {

        totalElement.textContent =
            stats.totalInspections;

    }


    // -------------------------------------------------
    // Defective PCBs
    // -------------------------------------------------

    const defectiveElement =
        document.getElementById(
            "defectivePcbs"
        );


    if (defectiveElement) {

        defectiveElement.textContent =
            stats.defectivePcb;

    }


    // -------------------------------------------------
    // Normal PCBs
    // -------------------------------------------------

    const normalElement =
        document.getElementById(
            "normalPcbs"
        );


    if (normalElement) {

        normalElement.textContent =
            stats.normalPcb;

    }


    // -------------------------------------------------
    // Total Defects
    // -------------------------------------------------

    const defectsElement =
        document.getElementById(
            "totalDefects"
        );


    if (defectsElement) {

        defectsElement.textContent =
            stats.totalDefects;

    }

}


// =====================================================
// Load Dashboard Statistics
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        displayDashboardStats();

    }
);