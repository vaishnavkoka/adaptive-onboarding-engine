// Adaptive Onboarding Engine - Frontend JavaScript
let currentAnalysis = null;
let gapChart = null;

// File input handlers
document.getElementById('resumeFile').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        console.log('Resume file selected:', file.name);
        document.getElementById('resumeFileName').textContent = '⏳ Processing...';
        const text = await extractTextFromFile(file);
        if (text) {
            document.getElementById('resume').value = text;
            document.getElementById('resumeFileName').textContent = `✓ Loaded: ${file.name} (${text.length} chars)`;
        }
    }
});

document.getElementById('jobFile').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        console.log('Job file selected:', file.name);
        document.getElementById('jobFileName').textContent = '⏳ Processing...';
        const text = await extractTextFromFile(file);
        if (text) {
            document.getElementById('jobDescription').value = text;
            document.getElementById('jobFileName').textContent = `✓ Loaded: ${file.name} (${text.length} chars)`;
        }
    }
});

async function extractTextFromFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        console.log('Extracting text from:', file.name);
        const response = await fetch('/api/extract-text', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            console.error('Extraction error:', error);
            showError(`Failed to extract text: ${error.error || 'Unknown error'}`);
            return '';
        }
        
        const data = await response.json();
        if (data.success) {
            console.log('Text extracted successfully');
            return data.text;
        } else {
            console.error('Extraction failed:', data.error);
            showError(`Failed to extract text: ${data.error}`);
            return '';
        }
    } catch (error) {
        console.error('Error extracting text:', error);
        showError('Error reading file. Please try again or paste the content manually.');
        return '';
    }
}

// Form submission
document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const resume = document.getElementById('resume').value.trim();
    const jobDescription = document.getElementById('jobDescription').value.trim();
    const jobCategory = document.getElementById('jobCategory').value;
    const maxWeeks = parseInt(document.getElementById('maxWeeks').value);
    
    // Validation
    if (!resume || resume.length < 50) {
        showError('Resume must be at least 50 characters');
        return;
    }
    if (!jobDescription || jobDescription.length < 50) {
        showError('Job description must be at least 50 characters');
        return;
    }
    if (!jobCategory) {
        showError('Please select a job category');
        return;
    }
    
    // Show loading
    document.getElementById('inputSection').style.display = 'none';
    document.getElementById('loadingContainer').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorContainer').style.display = 'none';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                resume_text: resume,
                job_description: jobDescription,
                job_category: jobCategory,
                max_weeks: maxWeeks
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            showError(data.error || 'Analysis failed');
            document.getElementById('loadingContainer').style.display = 'none';
            document.getElementById('inputSection').style.display = 'block';
            return;
        }
        
        currentAnalysis = data.analysis;
        displayResults(data.analysis);
        
        document.getElementById('loadingContainer').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please try again.');
        document.getElementById('loadingContainer').style.display = 'none';
        document.getElementById('inputSection').style.display = 'block';
    }
});

function displayResults(analysis) {
    // Match score and gauge
    const matchScore = analysis.match_score;
    document.getElementById('matchScore').textContent = Math.round(matchScore);
    
    // Animate gauge circle
    const gaugeCircle = document.getElementById('gaugeCircle');
    const circumference = 2 * Math.PI * 90;
    const offset = circumference * (1 - matchScore / 100);
    gaugeCircle.style.strokeDashoffset = offset;
    
    // Match description
    let matchDesc = '';
    if (matchScore < 30) {
        matchDesc = 'You\'re starting your journey in this field. The pathway will help you build foundational skills.';
    } else if (matchScore < 60) {
        matchDesc = 'You have some relevant skills but significant gaps. Focus on targeted learning in key areas.';
    } else if (matchScore < 80) {
        matchDesc = 'You have a strong foundation. Fill remaining gaps to be fully prepared for this role.';
    } else {
        matchDesc = 'Excellent match! You\'re well-prepared for this position. Continue refining advanced skills.';
    }
    document.getElementById('matchDescription').textContent = matchDesc;
    
    // Skills counts
    const resumeAnalysis = analysis.resume_analysis;
    const jobAnalysis = analysis.job_description_analysis;
    const gapAnalysis = analysis.skill_gap_analysis;
    
    document.getElementById('yourSkillsCount').textContent = resumeAnalysis.total_unique_skills;
    document.getElementById('requiredSkillsCount').textContent = jobAnalysis.total_required_skills;
    document.getElementById('gapCount').textContent = gapAnalysis.total_gaps;
    document.getElementById('yourScore').textContent = Math.round(resumeAnalysis.skill_score);
    
    // Gap chart
    displayGapChart(gapAnalysis);
    
    // Gap details
    displayGapDetails(gapAnalysis);
    
    // Pathway information
    const pathway = analysis.learning_pathway;
    document.getElementById('totalModules').textContent = pathway.total_modules;
    document.getElementById('totalHours').textContent = Math.round(pathway.total_hours);
    document.getElementById('trainingWeeks').textContent = pathway.total_weeks;
    document.getElementById('successRate').textContent = Math.round(pathway.estimated_success_rate * 100);
    
    // Modules list
    displayModulesList(pathway.modules);
    
    // Recommendations
    displayRecommendations(analysis.recommendations);
    
    // Reasoning trace
    displayReasoningTrace(analysis.reasoning_trace);
    
    // Export buttons
    setupExportButtons(analysis);
}

function displayGapChart(gapAnalysis) {
    const ctx = document.getElementById('gapChart').getContext('2d');
    
    const data = {
        labels: ['Critical', 'Moderate', 'Minor', 'Extra Skills'],
        datasets: [{
            label: 'Skill Gaps',
            data: [
                gapAnalysis.critical_gaps,
                gapAnalysis.moderate_gaps,
                gapAnalysis.minor_gaps,
                gapAnalysis.extra_skills
            ],
            backgroundColor: [
                '#ef4444',
                '#f59e0b',
                '#3b82f6',
                '#10b981'
            ],
            borderColor: [
                '#dc2626',
                '#d97706',
                '#1e40af',
                '#059669'
            ],
            borderWidth: 2,
            borderRadius: 8
        }]
    };
    
    if (gapChart) {
        gapChart.destroy();
    }
    
    gapChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: { size: 14 }
                    }
                }
            }
        }
    });
}

function displayGapDetails(gapAnalysis) {
    const container = document.getElementById('gapDetails');
    
    if (gapAnalysis.gaps_detail.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No skill gaps identified. You\'re well-matched for this role!</p>';
        return;
    }
    
    // Separate gaps by category
    const critical = gapAnalysis.gaps_detail.filter(g => g.category === 'critical');
    const moderate = gapAnalysis.gaps_detail.filter(g => g.category === 'moderate');
    const minor = gapAnalysis.gaps_detail.filter(g => g.category === 'minor');
    const extra = gapAnalysis.gaps_detail.filter(g => g.category === 'extra');
    
    let html = '';
    
    // Helper function to render gap items
    const renderGapItem = (gap) => {
        const categoryColor = {
            'critical': '#ef4444',
            'moderate': '#f59e0b',
            'minor': '#3b82f6',
            'extra': '#10b981'
        };
        
        const bgColor = categoryColor[gap.category] || '#6b7280';
        
        return `
            <div class="gap-item detailed-gap" style="border-left: 4px solid ${bgColor};">
                <div class="gap-header-compact">
                    <div class="gap-skill-name-compact">${gap.skill}</div>
                    <span class="gap-category-badge-compact" style="background-color: ${bgColor};">${gap.severity_label}</span>
                </div>
                <div class="gap-levels-compact">
                    <span class="level-label">Current:</span> <strong>${gap.current_level || 'none'}</strong>
                </div>
                <div class="gap-levels-compact">
                    <span class="level-label">Required:</span> <strong>${gap.target_level}</strong>
                </div>
                <div class="gap-severity-bar">
                    <div class="severity-progress" style="width: ${gap.gap_severity_percent}%; background-color: ${bgColor};"></div>
                </div>
                <p class="gap-severity-text-compact">${gap.gap_severity_percent}% Gap</p>
            </div>
        `;
    };
    
    // Display critical gaps first
    if (critical.length > 0) {
        html += '<div class="gap-section"><h4 style="color: #ef4444; margin-bottom: 1rem;">🔴 Critical Gaps (Highest Priority)</h4>';
        html += '<div class="gap-grid">';
        critical.forEach(gap => {
            html += renderGapItem(gap);
        });
        html += '</div></div>';
    }
    
    // Display moderate gaps
    if (moderate.length > 0) {
        html += '<div class="gap-section"><h4 style="color: #f59e0b; margin-bottom: 1rem;">🟠 Moderate Gaps (Important)</h4>';
        html += '<div class="gap-grid">';
        moderate.forEach(gap => {
            html += renderGapItem(gap);
        });
        html += '</div></div>';
    }
    
    // Display minor gaps
    if (minor.length > 0) {
        html += '<div class="gap-section"><h4 style="color: #3b82f6; margin-bottom: 1rem;">🔵 Minor Gaps (Nice to Have)</h4>';
        html += '<div class="gap-grid">';
        minor.forEach(gap => {
            html += renderGapItem(gap);
        });
        html += '</div></div>';
    }
    
    // Display extra skills
    if (extra.length > 0) {
        html += '<div class="gap-section"><h4 style="color: #10b981; margin-bottom: 1rem;">✅ Extra Skills (Bonus)</h4>';
        html += '<div class="gap-grid">';
        extra.forEach(gap => {
            html += renderGapItem(gap);
        });
        html += '</div></div>';
    }
    
    container.innerHTML = html;
}

function displayModulesList(modules) {
    const container = document.getElementById('modulesList');
    
    if (modules.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No additional modules recommended.</p>';
        return;
    }
    
    let html = '';
    modules.forEach((module, index) => {
        const difficultyClass = `difficulty-${module.difficulty.toLowerCase()}`;
        const prereqHtml = module.prerequisites && module.prerequisites.length > 0
            ? `<div class="module-prereq"><strong>Prerequisites:</strong> ${module.prerequisites.join(', ')}</div>`
            : '';
        
        html += `
            <div class="module-item">
                <div class="module-header">
                    <span class="module-name">${index + 1}. ${module.name}</span>
                    <span class="module-difficulty ${difficultyClass}">${module.difficulty}</span>
                </div>
                <div class="module-info">
                    <span>📚 ${module.skill}</span>
                    <span>⏱️ ${module.duration_hours} hours</span>
                </div>
                ${prereqHtml}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function displayRecommendations(recommendations) {
    // Immediate actions
    const immediateActions = document.getElementById('immediateActions');
    immediateActions.innerHTML = recommendations.immediate_actions
        .map(action => `<li>${action}</li>`)
        .join('');
    
    // Strengths
    const strengthsList = document.getElementById('strengthsList');
    strengthsList.innerHTML = recommendations.strengths_to_leverage
        .map(strength => `<li>${strength}</li>`)
        .join('');
    
    // Areas to develop
    const areasList = document.getElementById('areasList');
    areasList.innerHTML = recommendations.areas_to_develop
        .map(area => `<li>${area}</li>`)
        .join('');
}

function displayReasoningTrace(traces) {
    document.getElementById('extractionLogic').textContent = traces.extraction_logic;
    document.getElementById('gapLogic').textContent = traces.gap_identification_logic;
    document.getElementById('pathwayLogic').textContent = traces.pathway_generation_logic;
    
    const decisionsHtml = traces.key_decisions
        .map(decision => `<li>${decision}</li>`)
        .join('');
    
    document.getElementById('traceDecisions').innerHTML = `
        <strong style="display: block; margin-bottom: 0.5rem;">Key Decisions:</strong>
        <ul style="list-style-position: inside; color: var(--text-secondary);">
            ${decisionsHtml}
        </ul>
    `;
}

function setupExportButtons(analysis) {
    document.getElementById('exportCsvBtn').addEventListener('click', () => {
        exportAsCSV(analysis);
    });
    
    document.getElementById('downloadReportBtn').addEventListener('click', () => {
        downloadReport(analysis);
    });
}

function exportAsCSV(analysis) {
    const pathway = analysis.learning_pathway;
    const modules = pathway.modules;
    
    let csv = 'Module ID,Module Name,Skill Area,Difficulty,Duration (hours),Prerequisites\n';
    
    modules.forEach(module => {
        const prereqs = (module.prerequisites || []).join('; ') || 'None';
        csv += `"${module.id}","${module.name}","${module.skill}",${module.difficulty},${module.duration_hours},"${prereqs}"\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `learning_pathway_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function downloadReport(analysis) {
    const reportText = generateReportText(analysis);
    const blob = new Blob([reportText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `onboarding_analysis_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function generateReportText(analysis) {
    const lines = [
        '================================================================================',
        'ADAPTIVE ONBOARDING ANALYSIS REPORT',
        '================================================================================',
        `Generated: ${analysis.timestamp}`,
        `Target Position Category: ${analysis.job_category}`,
        '',
        'OVERALL FIT ASSESSMENT',
        '-'.repeat(80),
        `Match Score: ${analysis.match_score.toFixed(1)}%`,
        '',
        'YOUR CURRENT SKILLS',
        '-'.repeat(80),
        `Technical Skills: ${analysis.resume_analysis.technical_skills.slice(0, 10).join(', ')}${analysis.resume_analysis.technical_skills.length > 10 ? ` ... and ${analysis.resume_analysis.technical_skills.length - 10} more` : ''}`,
        `Soft Skills: ${analysis.resume_analysis.soft_skills.slice(0, 5).join(', ')}${analysis.resume_analysis.soft_skills.length > 5 ? ` ... and ${analysis.resume_analysis.soft_skills.length - 5} more` : ''}`,
        `Overall Skill Score: ${analysis.resume_analysis.skill_score.toFixed(1)}/100`,
        '',
        'SKILL GAP ANALYSIS',
        '-'.repeat(80),
        `Total Skill Gaps: ${analysis.skill_gap_analysis.total_gaps}`,
        `  - Critical: ${analysis.skill_gap_analysis.critical_gaps}`,
        `  - Moderate: ${analysis.skill_gap_analysis.moderate_gaps}`,
        `  - Minor: ${analysis.skill_gap_analysis.minor_gaps}`,
        '',
        'PERSONALIZED LEARNING PATHWAY',
        '-'.repeat(80),
        `Total Modules: ${analysis.learning_pathway.total_modules}`,
        `Total Hours: ${analysis.learning_pathway.total_hours}`,
        `Estimated Duration: ${analysis.learning_pathway.total_weeks} weeks`,
        `Estimated Success Rate: ${(analysis.learning_pathway.estimated_success_rate * 100).toFixed(1)}%`,
        '',
        'RECOMMENDATIONS',
        '-'.repeat(80),
        ...analysis.recommendations.immediate_actions.map(a => `→ ${a}`),
        '',
        'Strengths to Leverage:',
        ...analysis.recommendations.strengths_to_leverage.map(s => `  ✓ ${s}`),
        '',
        'Areas to Develop:',
        ...analysis.recommendations.areas_to_develop.map(a => `  • ${a}`),
        '',
        `Training Timeline: ${analysis.recommendations.timeline_estimate}`,
        '',
        '================================================================================',
    ];
    
    return lines.join('\n');
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorContainer').style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
