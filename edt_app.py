import streamlit as st
from openai import OpenAI
import os


os.environ['OPENAI_API_KEY'] = st.secrets["openai"]["api_key"]
client = OpenAI()

def check_password():
    """Returns `True` if the user entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["security"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False
            
    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True
    
def generate_email(sender, recipient, template_type, previous_email, tone, topics, language):
    topics_text = "\n".join([f"- {topic}" for topic in topics])
    previous_email_text = f"\n\nPrevious Email Thread:\n{previous_email}" if previous_email else ""
    
    prompt = (
        f"You are an AI assistant that generates personalized email drafts. "
        f"Create an email from {sender['name']} ({sender['job_title']}, {sender['email']}, {sender.get('telephone', '')}) "
        f"to {recipient['name']} ({recipient.get('email', '')}, {recipient.get('company', '')}). "
        f"The email is a {template_type} type, written in a {tone} tone. "
        f"Cover the following topics:\n{topics_text}{previous_email_text}\n\n"
        f"Please format the email appropriately with a subject, greeting, body, and closing."
    )

    system_content = (
        "You are an AI assistant specializing in generating well-crafted, personalized email drafts. "
        "Your task is to create an effective email based on the user's inputs. "
        "Ensure that the email is structured with a subject, greeting, body, and closing. "
        "Use appropriate language, tone, and formatting suited to the selected template type (e.g., Welcome, Follow-up, Reply, Sales/Marketing/Outreach). "
        "Adhere to the tone specified by the user (Friendly, Professional, Serious, Casual). "
        "Incorporate the topics provided by the user, ensuring they are clearly addressed in the email content. "
        "If a previous email thread is supplied, integrate its context seamlessly into the email. "
        "The email should be written in the language specified by the user, adhering to the respective spelling and grammar conventions. "
        "Available languages include English (UK or US), French, Portuguese, Spanish, German, Italian, Turkish, Japanese, Chinese, Vietnamese, Korean, Russian, Persian, Arabic, Urdu, Hindi, or Tamil."
    )

    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
    )
    
    email = completion.choices[0].message.content
    return email

def main():
    if not check_password():
        return

    # Page Layout
    st.set_page_config(
        page_title="Personalized Email Drafting Tool",
        page_icon="✉️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Logo and title
    logo_url = "https://www.keg.com/hubfs/keg_left_Sharp.svg"
    st.image(logo_url, width=200)
    st.title("Personalized Email Drafting Tool")

    # Input Form
    st.header("Sender Information")
    sender_name = st.text_input("Sender Name")
    sender_job_title = st.text_input("Sender Job Title")
    sender_email = st.text_input("Sender Email Address")
    sender_telephone = st.text_input("Sender Telephone (Optional)")

    st.header("Recipient Information")
    recipient_name = st.text_input("Recipient Name")
    recipient_email = st.text_input("Recipient Email Address", max_chars=50)
    recipient_company = st.text_input("Recipient Company (Optional)")

    st.header("Email Details")
    template_type = st.selectbox("Template Type", ["Welcome", "Follow-up", "Reply", "Sales/Marketing/Outreach"])
    previous_email = st.text_area("Previous Email History (Optional)")
    tone = st.selectbox("Tone of the Email", ["Friendly", "Professional", "Serious", "Casual"])
    language = st.selectbox("Language", ["English (UK)", "English (US)", "French", "Portuguese", "Spanish", "German", "Italian", "Turkish", "Japanese", "Chinese", "Vietnamese", "Korean", "Russian", "Persian", "Arabic", "Urdu", "Hindi", "Tamil"])
    topics = st.text_area("Topics to Cover (separate points by new lines)").split('\n')

    run_button = st.button("Generate Email")
    
    if run_button:
        sender = {
            'name': sender_name,
            'job_title': sender_job_title,
            'email': sender_email,
            'telephone': sender_telephone
        }
        recipient = {
            'name': recipient_name,
            'email': recipient_email,
            'company': recipient_company
        }

        email = generate_email(sender, recipient, template_type, previous_email, tone, topics, language)
        
        st.markdown("---")
        st.header("Generated Email")
        st.text_area("Draft Email", value=email, height=300)
        st.markdown("---")
        st.write("Thank you for using the Personalized Email Drafting Tool!")
    else:
        st.write("Fill in the details and click the 'Generate Email' button.")

if __name__ == "__main__":
    main()
