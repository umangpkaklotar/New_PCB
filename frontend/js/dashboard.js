// =====================================================
// PCB AI Inspection System
// Dashboard Statistics
// =====================================================


// =====================================================
// Get Stored Statistics
// =====================================================

function getInspectionStats() {

    const stats = {

        totalInspections:
            Number(
                localStorage.getItem(
                    "pcb_total_inspections"
                )
            ) || 0,


        defectivePcb:
            Number(
                localStorage.getItem(
                    "pcb_defective_inspections"
                )
            ) || 0,


        normalPcb:
            Number(
                localStorage.getItem(
                    "pcb_normal_inspections"
                )
            ) || 0,


        totalDefects:
            Number(
                localStorage.getItem(
                    "pcb_total_defects"
                )
            ) || 0

    };


    return stats;
}


// =====================================================
// Display Statistics on Dashboard
// =====================================================

function displayDashboardStats() {

    const stats =
        getInspectionStats();


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