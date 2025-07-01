# 🧩 Contributing to This Project

Thank you for taking the time to contribute! <br/>
Your help improves the quality and capabilities of this project, and we appreciate every bug report, feature request, and code contribution.

---

## 🚀 Getting Started

1. **Fork the repository** to your GitHub account.

2. **Clone your forked repository**

   ```bash
   git clone https://github.com/your-username/your-fork.git
   cd your-fork
   ```

3. **Create your branch**

   ```bash
   git checkout -b feature/your-idea
   ```

4. **Create a virtual environment** and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .  # Builds the package locally in editable mode
   ```

5. **Run PromptShell**

   ```bash
   promptshell
   ```

   **Run individual files using**: `python -m promptshell.<file_name>`

   > Replace <file_name> with the name of the module (without .py). <br/>
   > For example: python -m promptshell.main

6. **Commit changes**

   ```bash
   git commit -m "Add your feature"
   ```

7. **Push to the branch**

   ```bash
   git push origin feature/your-idea
   ```

8. **Open a Pull Request**

---

## 🛠 How to Contribute

### 🐛 Reporting Bugs

- Clearly describe the problem.
- Include a minimal reproducible example if possible.
- Mention environment details (OS, Python version, etc.).

### 💡 Requesting Features

- Explain why the feature is needed.
- Suggest potential use cases and examples.

### 👨‍💻 Submitting Code

- Create a feature branch:

  ```bash
  git checkout -b feature/your-feature-name
  ```

- Commit with clear messages.
- Push to your fork and submit a **Pull Request (PR)**.

---

## ✅ Code Guidelines

- **Linting**: Follow PEP8. Use `flake8` or `black` for formatting.
- **Typing**: Use Python type hints where applicable.
- **Testing**: Add/modify test cases under the `tests/` directory.
- **Docs**: Update `README.md` or docstrings if your changes affect usage.

---

## 📦 Pull Request Process

1. Ensure your branch is **rebased** with `main`.
2. Clearly describe what your PR does and why.
3. Link to any relevant issues in the description.
4. Be open to feedback and revisions.

---

## 🐞 Reporting Issues

When opening an issue, **use the provided templates**:

- `Bug report`
- `Feature request`
- `Performance concern`
- `Documentation error`

This helps us triage and respond faster.

---

## 🤝 Community Standards

We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
Be respectful, constructive, and supportive in all interactions.

---

## 🙌 Acknowledgement

Thanks again for contributing! Every improvement helps make this project better for everyone. Let’s build something amazing together 🚀
