from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
import re

app = Flask(__name__)

required_skills = {
    "Python Developer": [
        "Python", "SQL", "Flask", "Django", "Git"
    ],
    "Web Developer": [
        "HTML", "CSS", "JavaScript", "React", "Git"
    ],
    "AI ML Engineer": [
        "Python", "Machine Learning", "Deep Learning",
        "TensorFlow", "SQL"
    ],
    "Full Stack Developer": [
        "HTML", "CSS", "JavaScript", "Python",
        "SQL", "React", "Flask"
    ]
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/results")
def results():
    return render_template("results.html")


@app.route("/analyze", methods=["POST"])
def analyze_resume():

    # Check uploaded file
    if "resume" not in request.files:
        return jsonify({
            "error": "Please upload your resume"
        }), 400

    resume = request.files["resume"]
    job_role = request.form.get("jobRole")

    github = request.form.get("github", "").strip()
    linkedin = request.form.get("linkedin", "").strip()

    if resume.filename == "":
        return jsonify({
            "error": "No resume selected"
        }), 400

    if not job_role:
        return jsonify({
            "error": "Please select a job role"
        }), 400

    if not resume.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Please upload a PDF file"
        }), 400

    if job_role not in required_skills:
        return jsonify({
            "error": "Invalid job role"
        }), 400

    try:
        # Read PDF
        pdf = PdfReader(resume.stream)

        resume_text = ""

        for page in pdf.pages:
            resume_text += (page.extract_text() or "") + "\n"

        if not resume_text.strip():
            return jsonify({
                "error": "No readable text found in the PDF."
            }), 400

        # Skills Analysis
        skills = required_skills[job_role]
        resume_lower = resume_text.lower()

        found_skills = [
            skill for skill in skills
            if skill.lower() in resume_lower
        ]

        missing_skills = [
            skill for skill in skills
            if skill.lower() not in resume_lower
        ]

        match_percentage = round(
            len(found_skills) / len(skills) * 100
        ) if skills else 0

        # Normalize section headings
        def normalize_heading(text):
            text = text.lower().strip()
            text = re.sub(r"[^a-z0-9 ]", " ", text)
            text = re.sub(r"\s+", " ", text)
            return text.strip()

        # All supported headings
        section_headings = {
            "projects": [
                "projects",
                "project"
            ],
            "internships": [
                "internships",
                "internship",
                "internship experience"
            ],
            "activities": [
                "activities",
                "extra curricular activities",
                "extracurricular activities",
                "extra curricular",
                "co curricular activities",
                "hackethons",
                "hackathons",
                "hackathon"
            ],
            "certifications": [
                "certifications",
                "certificates",
                "certification",
                "certifications courses",
                "certifications and courses"
            ]
        }

        all_headings = [
            heading
            for headings in section_headings.values()
            for heading in headings
        ]

        all_headings.extend([
            "education",
            "skills",
            "technical skills",
            "personal skills",
            "experience",
            "work experience",
            "achievements",
            "summary",
            "professional summary",
            "objective",
            "tools used"
        ])

        # Extract content under a heading
        def extract_section(text, headings):
            lines = text.splitlines()
            section_lines = []
            capturing = False

            target_headings = {
                normalize_heading(h) for h in headings
            }

            normalized_all_headings = {
                normalize_heading(h) for h in all_headings
            }

            for line in lines:
                clean_line = line.strip()

                if not clean_line:
                    continue

                normalized_line = normalize_heading(clean_line)

                # Start capturing after target heading
                if normalized_line in target_headings:
                    capturing = True
                    continue

                # Stop at another section heading
                if capturing and normalized_line in normalized_all_headings:
                    break

                if capturing:
                    section_lines.append(clean_line)

            return section_lines

        # Extract Projects
        projects = extract_section(
            resume_text,
            section_headings["projects"]
        )

        # Extract Internships
        internships = extract_section(
            resume_text,
            section_headings["internships"]
        )

        # Extract Activities
        activities = extract_section(
            resume_text,
            section_headings["activities"]
        )

        # Extract Hackathons separately
        hackathons = extract_section(
            resume_text,
            ["hackethons", "hackathons", "hackathon"]
        )

        # Combine activities and hackathons
        activities = list(dict.fromkeys(
            activities + hackathons
        ))

        # Extract Certifications
        certifications = extract_section(
            resume_text,
            section_headings["certifications"]
        )

        # Resume Improvement Tips
        improvement_tips = []

        if missing_skills:
            improvement_tips.append(
                "Consider learning and adding these relevant skills: "
                + ", ".join(missing_skills)
            )
        else:
            improvement_tips.append(
                "Your resume mentions all the required skills for this role."
            )

        if not projects:
            improvement_tips.append(
                "Add a Projects section describing your academic or personal projects."
            )

        if not internships:
            improvement_tips.append(
                "If you have completed internships, include their details in your resume."
            )

        if not certifications:
            improvement_tips.append(
                "Consider adding relevant certifications you have completed."
            )

        if not activities:
            improvement_tips.append(
                "Include relevant activities such as hackathons, workshops, or volunteering, if applicable."
            )

        if "education" not in resume_lower:
            improvement_tips.append(
                "Include an Education section with your degree and college details."
            )

        if "summary" not in resume_lower:
            improvement_tips.append(
                "Consider adding a short professional summary describing your skills and career goals."
            )

        if match_percentage < 50:
            improvement_tips.append(
                "Review the job requirements and highlight relevant skills and projects in your resume."
            )

        # Return analysis results
        return jsonify({
            "message": "Resume analyzed successfully!",
            "job_role": job_role,
            "skills_found": found_skills,
            "missing_skills": missing_skills,
            "match_percentage": match_percentage,
            "github": github,
            "linkedin": linkedin,
            "projects": projects,
            "internships": internships,
            "activities": activities,
            "certifications": certifications,
            "improvement_tips": improvement_tips
        })

    except Exception as e:
        return jsonify({
            "error": "Unable to read the PDF: " + str(e)
        }), 400


if __name__ == "__main__":
    app.run(debug=True)