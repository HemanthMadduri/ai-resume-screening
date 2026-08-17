/**
 * TalentAI ATS - Charts & SVG Visualizations (Vanilla JS)
 * Zero external library dependencies.
 */

const ATSCharts = {
    /**
     * Render an animated circular score gauge using SVG.
     * @param {number} score - Score value between 0 and 100
     * @param {number} size - Pixel diameter of gauge (default 44)
     * @returns {string} SVG HTML string
     */
    renderScoreRing(score, size = 44) {
        const strokeWidth = 4;
        const radius = (size - strokeWidth) / 2;
        const circumference = 2 * Math.PI * radius;
        const clampedScore = Math.min(100, Math.max(0, score || 0));
        const offset = circumference - (clampedScore / 100) * circumference;

        let strokeColor = '#ef4444'; // Red (< 60)
        if (clampedScore >= 80) strokeColor = '#10b981'; // Green
        else if (clampedScore >= 60) strokeColor = '#f59e0b'; // Amber

        return `
            <div class="score-ring-wrapper" style="position: relative; width: ${size}px; height: ${size}px; display: inline-flex; align-items: center; justify-content: center;">
                <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" style="transform: rotate(-90deg);">
                    <circle cx="${size / 2}" cy="${size / 2}" r="${radius}" fill="none" stroke="var(--border-color)" stroke-width="${strokeWidth}" />
                    <circle cx="${size / 2}" cy="${size / 2}" r="${radius}" fill="none" stroke="${strokeColor}" stroke-width="${strokeWidth}"
                        stroke-dasharray="${circumference}" stroke-dashoffset="${offset}" stroke-linecap="round" style="transition: stroke-dashoffset 0.6s ease;" />
                </svg>
                <span style="position: absolute; font-size: ${size > 50 ? '14px' : '11.5px'}; font-weight: 800; color: var(--text-primary); font-family: var(--font-sans);">
                    ${Math.round(clampedScore)}%
                </span>
            </div>
        `;
    },

    /**
     * Render a horizontal score bar element.
     * @param {string} label 
     * @param {number} score (0-100)
     * @param {string} weightText
     * @param {string} colorClass
     * @returns {string} HTML string
     */
    renderScoreBar(label, score, weightText = '', colorClass = 'var(--primary)') {
        const clampedScore = Math.min(100, Math.max(0, score || 0));
        return `
            <div class="score-bar-item">
                <div class="score-bar-header">
                    <span>${label} <small style="color: var(--text-muted);">(${weightText})</small></span>
                    <strong style="color: ${colorClass};">${clampedScore.toFixed(1)}%</strong>
                </div>
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width: ${clampedScore}%; background-color: ${colorClass};"></div>
                </div>
            </div>
        `;
    }
};

window.ATSCharts = ATSCharts;
