# DocumentMint: AI-Powered Document Generation

DocumentMint is an innovative AI-powered application designed to streamline the process of creating professional documents. By leveraging advanced language models and a user-friendly interface, DocumentMint allows users to generate high-quality documents with ease.

## 🌟 Features

* **AI-Powered Questionnaire:** Intelligently gather information from users to create tailored documents.
* **Dynamic Document Generation:** Automatically generate documents based on user responses.
* **Customizable Templates:** Support for various document types and templates.
* **Interactive UI:** Built with Streamlit for a seamless user experience.
* **LLM Integration:** Utilizes state-of-the-art language models for content generation.

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aousabdo/documint_aous.git 
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**
   * Create a `.env` file in the root directory and add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ANTHROPIC_API_KEY=your_anthropic_api_key_here 
     ```

4. **Run the application:**
   ```bash
   streamlit run app/main.py 
   ```

## 🖥️ Usage

1. Navigate to the application in your web browser (typically http://localhost:8501).
2. Select the type of document you want to create.
3. Answer the AI-generated questionnaire.
4. Review and edit the generated document.
5. Download or export your finalized document.

## 🧠 How It Works

DocumentMint uses a sophisticated questionnaire system to gather information from users. The core of this system is implemented in the `create_questionnaire` function:

```python
def create_questionnaire(...):
    # ... code for questionnaire logic ...
```

This function dynamically creates a questionnaire based on predefined questions, handles user input, and manages required fields. The collected responses are then used to generate the document using AI language models.

## 🛠️ Customization

You can customize document templates and questionnaires by modifying the relevant files in the `templates/` directory. The application supports various document types, including:

* Statement of Work (SOW)
* Project Proposals
* Legal Agreements
* And more!

## 🤝 Contributing

We welcome contributions to DocumentMint! Here's how you can help:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/AmazingFeature`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
5. Push to the branch (`git push origin feature/AmazingFeature`).
6. Open a Pull Request.

Please ensure your code adheres to our coding standards and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

* OpenAI for their powerful language models
* Streamlit for the amazing web application framework
* All contributors and users of DocumentMint

## 📞 Contact

For any questions or support, please open an issue on this repository or contact the maintainers directly.

---

Happy document creation with DocumentMint! 📝✨ 

