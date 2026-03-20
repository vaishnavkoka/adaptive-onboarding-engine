# Video Demonstration Script (2-3 Minutes)

## Quick Recording Guide

**Duration**: 2-3 minutes
**Format**: Screen recording (OBS Studio, Screenflow, or built-in tools)
**Audio**: Clear narration
**Quality**: 1080p or higher recommended

### Setup Instructions

```bash
# 1. Ensure server is running
ps aux | grep "python app.py" | grep -v grep

# 2. If not running, start it:
cd /home/vaishnavkoka/RE4BDD/AI-Adaptive Onboarding Engine
/home/vaishnavkoka/RE4BDD/AI-Adaptive Onboarding Engine/venv/bin/python app.py

# 3. Open browser to:
http://localhost:5000
# OR for network access:
http://10.0.118.247:5000
```

---

## VIDEO SCRIPT (Read this while recording)

### [INTRO - 0:00-0:15] (15 seconds)

**Narration**: 
"Welcome to the AI-Adaptive Onboarding Engine - an intelligent system that creates personalized learning pathways for new employees. Instead of the traditional one-size-fits-all approach, our system analyzes your skills and generates a customized training roadmap in seconds."

**Visual**: Show the home page with header visible

---

### [SECTION 1 - 0:15-0:45] File Upload & Skill Extraction (30 seconds)

**Narration**: 
"First, upload your resume. Click on the resume upload button and select a PDF, Word document, or text file. The system will instantly extract your skills."

**Actions to perform on screen**:
1. Point to "📁 Upload Resume" button
2. Click it to open file picker
3. Select a PDF resume file (show: `problem_statement.pdf` or any PDF)
4. Wait for extraction message: "✓ Loaded: filename.pdf"
5. Show extracted text in textarea

**Narration continues**:
"Next, upload the job description for the position you're targeting. Click the job description upload button and select another file."

**Actions**:
6. Point to "📁 Upload Job Description" button
7. Click and select a PDF/DOCX file
8. Show the extraction confirmation
9. Optionally paste sample job description text if file loading is slow

---

### [SECTION 2 - 0:45-1:15] Form Submission & Analysis (30 seconds)

**Narration**:
"Now we'll select the job category. This helps the system understand the domain-specific skills needed. We have 24 job categories available."

**Actions**:
1. Click "Job Category" dropdown
2. Show the list of 24 categories briefly:
   "ACCOUNTANT, ADVOCATE, AGRICULTURE... ENGINEERING, FINANCE... up to TEACHER"
3. Select one category (e.g., "ENGINEERING")

**Narration**:
"Set the maximum training duration - this tells the system how many weeks you have to learn new skills."

**Actions**:
4. Show "Maximum Training Duration" field
5. Keep or change the value (e.g., 12 weeks)
6. Click "📊 Analyze Skills" button

**Narration**:
"Now watch as the system analyzes your resume and job description, identifies skill gaps, and generates a personalized learning pathway."

**Actions**:
7. Show loading spinner appearing
8. Wait for results to load

---

### [SECTION 3 - 1:15-2:00] Results Visualization (45 seconds)

**Narration**:
"The analysis is complete! Here's the personalized results. The first visualization shows your overall match score - this is the percentage of skills you already have for the target position."

**Actions**:
1. Point to the match gauge (circular progress indicator)
2. Show the percentage score
3. Explain the match description displayed

**Narration**:
"Below the match score, you'll see your skills overview - a breakdown of what you already know and what you need to learn."

**Actions**:
4. Scroll down to "Skills Overview"
5. Show the breakdown chart or text

**Narration**:
"The most important part is your personalized learning pathway. This shows exactly what you need to learn, in the recommended order, with difficulty levels and time estimates."

**Actions**:
6. Scroll to "Learning Pathway" section
7. Point to and read a few modules:
   - "JavaScript Fundamentals - Beginner - 15 hours"
   - "React Advanced - Intermediate - 25 hours"
   - etc.
8. Show that modules are ordered by risk and complexity

**Narration**:
"Each module shows prerequisites, so you know what skills you need first. The system ensures you build knowledge progressively."

**Actions**:
9. Click on a module to show details (if expandable)
10. Point to prerequisites, difficulty, and time estimate

---

### [SECTION 4 - 2:00-2:30] Additional Features (30 seconds)

**Narration**:
"You can also export this pathway as a CSV file to track your progress in a spreadsheet or share it with trainers."

**Actions**:
1. Scroll to find "Export as CSV" button (if visible)
2. Click it to download
3. Say "The CSV now contains your complete learning pathway"

**Narration**:
"The system is completely grounded in reality with zero hallucinations - it only recommends modules from a predefined catalog of 50+ verified training modules. Every recommendation is transparent, showing how skills were extracted and why modules were prioritized."

**Actions**:
4. Scroll up to show "Reasoning Trace" section if available
5. Point to showed decisions/logic

**Narration**:
"The entire analysis happens in real-time, in under 5 seconds, whether you upload PDFs or paste text directly. The system supports PDF, Word documents, and plain text files."

---

### [OUTRO - 2:30-2:45] (15 seconds)

**Narration**:
"That's the AI-Adaptive Onboarding Engine! It dramatically reduces onboarding time while ensuring every employee gets exactly the training they need. The system is fully open-source, containerized with Docker, and ready for enterprise deployment."

**Actions**:
1. Show the GitHub link at bottom of page (or mention it)
2. End with confident smile

**Final text on screen** (optional overlay):
```
✅ Intelligent Skill Extraction (Keyword + LLM)
✅ Personalized Learning Pathways (Risk-Based Ordering)
✅ Zero Hallucinations (Catalog-Restricted)
✅ Full Transparency (Reasoning Trace)
✅ Enterprise-Ready

Try it live: http://10.0.118.247:5000
GitHub: https://github.com/vaishnavkoka/adaptive-onboarding-engine
```

---

## Recording Tips

### Do's ✅
- **Clear audio**: Speak slowly and clearly
- **Mouse speed**: Move cursor smoothly, not too fast
- **Zoom level**: Make sure text is readable (120-125% zoom if needed)
- **Pacing**: Give 1-2 seconds pause between major sections for understanding
- **Screen**: Resize browser window to ~1400x800 for good visibility
- **Lighting**: If using camera zoom, ensure good lighting

### Don'ts ❌
- Don't rush through sections (2-3 min is good, better slow than too fast)
- Don't show terminal commands (keep it user-facing only)
- Don't forget to smile/use friendly tone in narration
- Don't edit out the file upload (it's a key feature)
- Don't skip explaining why the pathway is personalized

### File Preparation
1. Have at least 2 PDF/DOCX files ready (resume + job description)
2. Or use sample text content ready to paste
3. Test server is running before recording starts
4. Have job descriptions with clear skill requirements

---

## Quick Demo Datasets

If you need sample files for recording, use:

**Sample Resume Text**:
```
Senior Full-Stack Engineer
8+ years experience

Skills:
- JavaScript, Python, Java
- React.js, Node.js, Django
- PostgreSQL, MongoDB
- Docker, Kubernetes, AWS
- Leadership, mentoring

Experience:
- Led team of 10 engineers
- Architected microservices platform
- 95% uptime production systems
```

**Sample Job Description Text**:
```
Full-Stack Developer - Remote

Required:
- 5+ years web development
- React.js & Node.js expertise
- SQL/NoSQL databases
- Docker & version control
- Team collaboration
- CI/CD pipelines (Jenkins/GitHub Actions)

Nice to have:
- GraphQL experience
- Kubernetes knowledge
- AWS/GCP experience
- Open source contributions

Salary: $130-160K
```

---

## Post-Recording Checklist

- [ ] Audio is clear and at good volume
- [ ] Screen is visible and readable
- [ ] Demo flows smoothly without jumps
- [ ] All 4 sections covered (Upload, Analyze, Results, Features)
- [ ] Duration is 2-3 minutes
- [ ] Thumbnail/Cover image shows the app
- [ ] Description includes GitHub link
- [ ] Upload to YouTube or platform of choice

---

## Alternative: Live Demo Option

Instead of pre-recorded, you can do a **live demo** to judges:

1. Open http://10.0.118.247:5000 on projector
2. Have files ready in file manager
3. Upload resume → Show extraction
4. Upload job description → Show extraction
5. Select category and click Analyze
6. Walk through results
7. Explain reasoning trace
8. Offer to answer questions

Live demos often impress more than videos!

---

## Estimated Recording Time
- Setup: 5 minutes
- First take: 3-5 minutes
- Re-recording (if needed): 3-5 minutes
- **Total: 10-20 minutes**

**Done!** 🎬 Ready to submit to hackathon
