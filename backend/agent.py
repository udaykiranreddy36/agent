from crewai import Crew, Task, Agent
from crewai_tools import SerperDevTool, FileReadTool
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Set environment variables (your existing API keys)
os.environ['SERPER_API_KEY'] = "e9a8d60c89669fdc40f7887c3a10feb5546e5520"
os.environ['OPENROUTER_API_KEY'] = "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"

# Initialize tools
search = SerperDevTool()
file_reader = FileReadTool()

# Your Enhanced Portfolio Agent with Knowledge Base
enhanced_portfolio_agent = Agent(
    llm="openrouter/meta-llama/llama-3.3-70b-instruct:free",
    role="Personal Portfolio Representative for Galma Uday Kiran Reddy",
    goal="Act as Uday Kiran's comprehensive digital representative with access to his resume, portfolio content, and project details to provide accurate, professional information to portfolio visitors, potential employers, and collaborators",
    backstory=f"""You are the digital representation of Galma Uday Kiran Reddy, an Information Technology student at Anurag University (2022-2026) with CGPA 8.05/10, based in Hyderabad, Telangana, India.

COMPREHENSIVE PERSONAL BACKGROUND:
- Email: galmauday@gmail.com | Phone: +91 8885496463
- Portfolio: galmauday.vercel.app
- University: Anurag University, B.Tech Information Technology
- Current Academic Standing: CGPA 8.05/10 (2022-2026)

TECHNICAL EXPERTISE:
- Programming Languages: C, Java, Python (NumPy, Pandas, Seaborn, Matplotlib, Plotly)
- Web Development: HTML, CSS, JavaScript, Tailwind CSS, Bootstrap, Angular, ReactJS, NextJS
- Databases: MySQL, MongoDB
- Frameworks: Django, Spring Boot, Flask, Streamlit
- UI/UX Tools: Figma, Canva
- Machine Learning: TensorFlow, Scikit-learn, XGBoost
- Data Analytics: PowerBI, MS Excel, Tableau, SQL

MAJOR UNIVERSITY PROJECTS:
1. Nomad Compass (Feb 2025) - All-in-one tourism platform with ML-based trip planner
2. Explainable AI Medical Diagnosis for Diabetes (Jan 2025) - Interactive health prediction app
3. Sustainable Fertilizer Usage Optimizer (Nov 2024) - Agricultural ML application

CERTIFICATIONS:
Java Spring Boot, Python Essentials 1&2, Java 11 Essentials, Java NPTEL, MongoDB, MATLAB

PERSONAL INTERESTS:
Swimming, Table Tennis, UI/UX Design, Data-Driven Projects, Cooking
Languages: English, Telugu, Hindi

PERSONALITY & COMMUNICATION STYLE:
- Professional yet approachable and conversational
- Technical expertise combined with clear explanations
- Passionate about AI/ML, web development, and solving real-world problems
- Enthusiastic about learning new technologies and building innovative solutions
- Perfect representative for engaging with potential employers, recruiters, and collaborators

You have access to detailed knowledge files containing his complete resume, portfolio content, and project descriptions. Always respond in first person as if you ARE Uday Kiran, using "I", "my", "me" etc.

RESPONSE FORMAT FOR WEB:
Keep responses concise but informative for web chat interface. Break long responses into paragraphs. Use natural language without excessive formatting.""",
    allow_delegation=False,
    tools=[search, file_reader],
    verbose=False,  # Set to False for production
)

# Portfolio Agent Class for Easy Integration
class PortfolioAgent:
    def __init__(self):
        self.agent = enhanced_portfolio_agent
        self.crew = None
        
        # File paths for knowledge base
        self.knowledge_files = {
            'resume': 'knowledge/resume.txt',
            'portfolio': 'knowledge/portfolio_content.txt',
            'projects': 'knowledge/projects_description.txt'
        }
        
        # Cache for frequently asked questions to improve response time
        self.faq_cache = {}
    
    def create_enhanced_task(self, visitor_question):
        """Create comprehensive task with access to all knowledge sources"""
        return Task(
            description=f"""
            VISITOR QUESTION: "{visitor_question}"
            
            You are responding as Galma Uday Kiran Reddy to a visitor on your portfolio website.
            
            KNOWLEDGE BASE ACCESS:
            You have access to comprehensive information through these files:
            1. Resume: {self.knowledge_files['resume']} - Complete academic and professional background
            2. Portfolio Content: {self.knowledge_files['portfolio']} - Website overview and technical skills
            3. Projects: {self.knowledge_files['projects']} - Detailed university project descriptions
            
            RESPONSE INSTRUCTIONS:
            1. Read relevant knowledge files using FileReadTool for accurate information
            2. For current information (job market, tech trends), use SerperDevTool for web search
            3. ALWAYS respond in FIRST PERSON as Uday Kiran ("I am", "My experience", "I have worked on", etc.)
            4. Be professional yet conversational for web chat interface
            5. Keep responses concise but informative (2-4 paragraphs max)
            6. Provide specific details from your actual background, projects, and skills
            7. For technical questions, demonstrate knowledge while keeping explanations accessible
            8. Be helpful and engaging, representing yourself well to potential employers
            
            RESPONSE STYLE:
            - Natural and conversational, not robotic
            - Professional but approachable
            - Specific and informative with real details
            - Enthusiastic about technology and learning
            - Web-friendly formatting (short paragraphs)
            """,
            expected_output="Natural, conversational first-person response as Uday Kiran, addressing the visitor's question with specific details from knowledge base. Keep it concise for web chat interface.",
            agent=self.agent,
        )
    
    def answer_question(self, question):
        """Enhanced answer with full knowledge access and caching"""
        # Simple caching for common questions
        question_key = question.lower().strip()
        if question_key in self.faq_cache:
            return self.faq_cache[question_key]
        
        task = self.create_enhanced_task(question)
        
        self.crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False  # Keep False for production
        )
        
        try:
            result = self.crew.kickoff()
            response = str(result).strip()
            
            # Cache common responses
            if len(question_key) > 10:  # Only cache substantial questions
                self.faq_cache[question_key] = response
            
            return response
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)[:100]}... Please try asking your question differently, and I'll do my best to help!"
            return error_message
    
    def get_quick_intro(self):
        """Get a brief introduction for first-time visitors"""
        return """Hi! I'm Uday Kiran, an Information Technology student at Anurag University with a passion for AI/ML and web development. 

I've built several exciting projects including a tourism platform with ML-based planning, an AI diabetes diagnosis tool, and agricultural optimization systems. My technical skills span Python, Java, React, Django, and machine learning frameworks.

Feel free to ask me about my projects, technical skills, education, or career goals!"""
    
    def get_contact_info(self):
        """Get contact information"""
        return """You can reach me through several ways:

📧 Email: galmauday@gmail.com
📱 Phone: +91 8885496463  
🌐 Portfolio: galmauday.vercel.app
📍 Location: Hyderabad, Telangana, India

I'm actively seeking internship and full-time opportunities in software development, AI/ML, or data analytics. Feel free to connect!"""

# Flask Integration Class
class FlaskPortfolioAgent:
    """Simplified version specifically for Flask API integration"""
    
    def __init__(self):
        self.agent = PortfolioAgent()
    
    def process_chat_message(self, message):
        """Process a single chat message and return response"""
        try:
            if not message or len(message.strip()) == 0:
                return {
                    'response': "Please ask me a question about my background, projects, or skills!",
                    'status': 'success'
                }
            
            # Handle common quick responses
            message_lower = message.lower().strip()
            
            if any(word in message_lower for word in ['hi', 'hello', 'hey']):
                response = self.agent.get_quick_intro()
            elif any(word in message_lower for word in ['contact', 'email', 'phone', 'reach']):
                response = self.agent.get_contact_info()
            else:
                response = self.agent.answer_question(message)
            
            return {
                'response': response,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'response': f"I apologize, but I'm having trouble responding right now. Please try again! Error: {str(e)[:50]}...",
                'status': 'error'
            }

# Demo and Testing Function (Updated for web integration)
def run_portfolio_demo():
    """Run a demonstration of the portfolio agent capabilities"""
    print("🚀 Initializing Uday Kiran's Portfolio Agent...")
    agent = PortfolioAgent()
    
    # Sample questions that visitors might ask
    sample_questions = [
        "Hi, tell me about yourself",
        "What are your technical skills?",
        "What projects have you worked on?",
        "Are you looking for job opportunities?",
        "How can I contact you?"
    ]
    
    print("📋 Portfolio Agent Demo - Web Chat Simulation")
    print("=" * 60)
    
    for i, question in enumerate(sample_questions, 1):
        print(f"\n🔹 Visitor: {question}")
        print("🤖 Uday:")
        response = agent.answer_question(question)
        print(response)
        print("-" * 60)

# Main execution
if __name__ == "__main__":
    # Test the agent
    print("🎯 Testing Uday Kiran's Portfolio Agent...")
    
    # Quick test
    agent = FlaskPortfolioAgent()
    test_result = agent.process_chat_message("Tell me about your projects")
    print("Test Response:", test_result)
    
    # Interactive mode
    print("\n" + "="*50)
    print("🎯 Uday Kiran's Portfolio Agent is Ready!")
    print("Ask me anything about my background, skills, projects, or career goals.")
    print("Type 'demo' to see sample Q&A, 'quit' to exit, or ask any question.\n")
    
    my_portfolio_agent = PortfolioAgent()
    
    while True:
        user_input = input("🔹 Your question: ").strip()
        
        if user_input.lower() == 'quit':
            print("👋 Thanks for visiting my portfolio! Feel free to reach out at galmauday@gmail.com")
            break
        elif user_input.lower() == 'demo':
            run_portfolio_demo()
        elif user_input:
            print("\n🤖 Uday's Response:")
            response = my_portfolio_agent.answer_question(user_input)
            print(response)
            print("\n" + "="*60 + "\n")
        else:
            print("Please ask a question or type 'quit' to exit.")



