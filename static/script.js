const form = document.getElementById("resumeForm");
const jobRole = document.getElementById("jobRole");
const requiredSkills = document.getElementById("requiredSkills");

// Required skills for each job role
const skills = {
    "Python Developer": [
        "Python",
        "Data Structures",
        "OOP",
        "SQL",
        "Flask",
        "Git"
    ],

    "Web Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Responsive Design",
        "Git"
    ],

    "AI ML Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "NumPy",
        "Pandas",
        "TensorFlow",
        "SQL",
        "Statistics"
    ],

    "Full Stack Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "Python",
        "SQL",
        "Flask",
        "Git"
    ]
};

// Display required skills
jobRole.addEventListener("change", function () {
    const selectedRole = jobRole.value;

    if (selectedRole && skills[selectedRole]) {
        requiredSkills.innerHTML = `
            <ul>
                ${skills[selectedRole]
                    .map(skill => `<li>${skill}</li>`)
                    .join("")}
            </ul>
        `;
    } else {
        requiredSkills.textContent =
            "Select a job role to view required skills.";
    }
});

// Analyze Resume
form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const resume = document.getElementById("resume").files[0];
    const selectedRole = jobRole.value;

    const github = document.getElementById("github").value;
    const linkedin = document.getElementById("linkedin").value;

    // Validate inputs
    if (!resume || !selectedRole) {
        alert("Please upload your resume and select a job role.");
        return;
    }

    // Validate PDF
    if (!resume.name.toLowerCase().endsWith(".pdf")) {
        alert("Please upload a PDF file.");
        return;
    }

    // Prepare form data
    const formData = new FormData();

    formData.append("resume", resume);
    formData.append("jobRole", selectedRole);
    formData.append("github", github);
    formData.append("linkedin", linkedin);

    // Disable button while analyzing
    const button = form.querySelector("button");
    button.disabled = true;
    button.textContent = "Analyzing...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Analysis failed.");
            return;
        }

        // Store analysis result
        sessionStorage.setItem(
            "analysisResult",
            JSON.stringify(result)
        );

        // Open results page
        window.location.href = "/results";

    } catch (error) {
        alert("Error connecting to the server.");
        console.error(error);

    } finally {
        button.disabled = false;
        button.textContent = "Analyze Resume";
    }
});