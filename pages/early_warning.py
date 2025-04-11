"""
Early Warning System for the Volcano Monitoring Dashboard.

This page handles subscriptions to volcano alerts via email and SMS, including subscription management
and a preview of the alerts that will be sent.
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from typing import Dict, List, Any

# Import utils
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import get_volcano_data, get_volcano_details, get_volcano_by_name
from utils.alerts import (
    init_db, subscribe_to_volcano, unsubscribe_from_volcano,
    get_subscriber_volcanoes, send_volcano_alert, get_subscription_plans
)

# Initialize database on first run
init_db()

def app():
    st.title("Volcano Early Warning System")
    
    # Check if Twilio credentials are available to show appropriate messages
    twilio_available = all([
        os.environ.get("TWILIO_ACCOUNT_SID"),
        os.environ.get("TWILIO_AUTH_TOKEN"),
        os.environ.get("TWILIO_PHONE_NUMBER")
    ])
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Subscribe to Alerts", 
        "Manage Subscriptions", 
        "Alert Preview", 
        "Subscription Plans"
    ])
    
    with tab1:
        display_subscription_form(twilio_available)
    
    with tab2:
        display_subscription_management()
    
    with tab3:
        display_alert_preview()
    
    with tab4:
        display_subscription_plans()


def display_subscription_form(twilio_available: bool = False):
    """Display the subscription form for volcano alerts."""
    st.header("Subscribe to Volcano Alerts")
    
    st.write("""
    Get notified when volcanic activity changes for the volcanoes you care about. 
    Free subscribers receive email alerts, while paid subscribers get both 
    email and SMS notifications.
    """)
    
    # Load volcano data
    volcano_data = get_volcano_data()
    volcano_names = volcano_data["name"].tolist()
    
    # Add volcano selector
    selected_volcano_name = st.selectbox(
        "Select a volcano to monitor:",
        options=volcano_names
    )
    
    # Get the selected volcano details
    selected_volcano = volcano_data[volcano_data["name"] == selected_volcano_name].iloc[0]
    volcano_id = selected_volcano.get("id", "unknown")
    
    # Show volcano current status
    alert_level = selected_volcano.get("alert_level", "Unknown")
    st.info(f"Current alert level for {selected_volcano_name}: **{alert_level}**")
    
    # Add form for subscription
    with st.form("subscription_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Email Address")
        
        # Show phone field with note about paid subscription
        phone = st.text_input(
            "Phone Number (SMS alerts - paid subscription only)",
            placeholder="+1234567890"
        )
        
        # Select subscription level
        subscription_options = ["Free", "Basic ($4.99/month)", "Premium ($9.99/month)"]
        subscription_display = st.radio(
            "Subscription Level",
            options=subscription_options
        )
        # Convert display name to database value
        subscription_level = subscription_display.lower().split()[0] if subscription_display else "free"
        
        # Alert threshold selection
        threshold_options = ["Warning", "Watch", "Advisory", "Normal"]
        alert_threshold = st.selectbox(
            "Alert me when level reaches or exceeds:",
            options=threshold_options,
            index=0
        )
        
        # Alert frequency
        frequency_options = ["Immediate", "Daily", "Weekly"]
        alert_frequency = st.selectbox(
            "Alert Frequency",
            options=frequency_options,
            index=0
        )
        
        # Submit button
        submit_button = st.form_submit_button("Subscribe")
        
        if submit_button:
            if not email:
                st.error("Email address is required.")
            elif not name:
                st.error("Name is required.")
            else:
                # Handle the subscription
                if subscription_level != "free" and not phone:
                    st.warning("Phone number is recommended for paid subscriptions to receive SMS alerts.")
                
                success, message = subscribe_to_volcano(
                    name=name,
                    email=email,
                    phone=phone,
                    volcano_id=volcano_id,
                    subscription_level=subscription_level,
                    alert_threshold=alert_threshold,
                    alert_frequency=alert_frequency
                )
                
                if success:
                    st.success(message)
                    if subscription_level != "free":
                        st.info("For a real application, this would redirect to a payment page.")
                    
                    # Show what alerts they'll receive
                    st.write(f"You will receive alerts when {selected_volcano_name} reaches {alert_threshold} level.")
                    if subscription_level == "free":
                        st.write("Free subscription: Email alerts only")
                    else:
                        st.write(f"{subscription_level.capitalize()} subscription: Email and SMS alerts")
                else:
                    st.error(message)
    
    # Warning about SMS if Twilio is not configured
    if not twilio_available:
        st.warning(
            "SMS alerts are currently in testing mode. In a production environment, "
            "you would receive real SMS messages for paid subscriptions."
        )


def display_subscription_management():
    """Display interface for managing existing subscriptions."""
    st.header("Manage Your Subscriptions")
    
    st.write("""
    View and manage your volcano alert subscriptions. Enter your email address to see
    the volcanoes you're monitoring and change your alert preferences.
    """)
    
    # Email lookup form
    email = st.text_input("Enter your email address:")
    lookup_button = st.button("Look Up Subscriptions")
    
    if lookup_button and email:
        # Get subscriptions for this email
        subscriptions = get_subscriber_volcanoes(email=email)
        
        if not subscriptions:
            st.info("No subscriptions found for this email address.")
        else:
            st.success(f"Found {len(subscriptions)} active subscriptions.")
            
            # Display subscription table
            volcano_data = get_volcano_data()
            
            # Create a list to hold the subscription info
            subscription_info = []
            
            for sub in subscriptions:
                volcano_id = sub["volcano_id"]
                # Find volcano name from ID
                volcano_row = volcano_data[volcano_data["id"] == volcano_id]
                volcano_name = volcano_row["name"].iloc[0] if not volcano_row.empty else "Unknown Volcano"
                
                subscription_info.append({
                    "Volcano": volcano_name,
                    "ID": volcano_id,
                    "Alert Threshold": sub["alert_threshold"],
                    "Frequency": sub["alert_frequency"]
                })
            
            # Display as a table
            if subscription_info:
                df = pd.DataFrame(subscription_info)
                st.dataframe(df)
                
                # Unsubscribe option
                st.subheader("Unsubscribe")
                volcano_to_remove = st.selectbox(
                    "Select a volcano to unsubscribe from:",
                    options=df["Volcano"].tolist()
                )
                
                if volcano_to_remove:
                    # Find the volcano ID
                    volcano_id_to_remove = df[df["Volcano"] == volcano_to_remove]["ID"].iloc[0]
                    
                    if st.button(f"Unsubscribe from {volcano_to_remove}"):
                        success, message = unsubscribe_from_volcano(email, volcano_id_to_remove)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)


def display_alert_preview():
    """Display a preview of what alert messages will look like."""
    st.header("Alert Preview")
    
    st.write("""
    See examples of the alert messages you will receive when a volcano's alert level changes.
    Email alerts include more detailed information, while SMS alerts are concise to fit within
    message limits.
    """)
    
    # Load volcano data
    volcano_data = get_volcano_data()
    volcano_names = volcano_data["name"].tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Select volcano for preview
        selected_volcano_name = st.selectbox(
            "Select a volcano:",
            options=volcano_names,
            key="preview_volcano"
        )
    
    with col2:
        # Select alert level for preview
        alert_level = st.selectbox(
            "Select alert level:",
            options=["Normal", "Advisory", "Watch", "Warning"],
            index=3  # Default to Warning for dramatic effect
        )
    
    # Get selected volcano data
    selected_volcano = volcano_data[volcano_data["name"] == selected_volcano_name].iloc[0].to_dict()
    
    # Override alert level for preview
    selected_volcano["alert_level"] = alert_level
    
    # Generate example alert message
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    alert_message = f"VOLCANO ALERT: {selected_volcano_name} is now at {alert_level} level. "
            
    if alert_level == "Warning":
        alert_message += "Immediate action may be required. Check dashboard for details."
    elif alert_level == "Watch":
        alert_message += "Be prepared for possible evacuation. Monitor situation closely."
    elif alert_level == "Advisory":
        alert_message += "Be aware of increased volcanic activity."
    else:
        alert_message += "Activity has returned to normal levels."
    
    alert_message += f" (Alert time: {current_time})"
    
    # Display example SMS
    st.subheader("SMS Alert Example")
    st.code(alert_message)
    
    # Display example email
    st.subheader("Email Alert Example")
    email_subject = f"Volcano Alert: {selected_volcano_name} - {alert_level}"
    
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: {'#cc0000' if alert_level == 'Warning' else '#ff9900' if alert_level == 'Watch' else '#33cc33' if alert_level == 'Normal' else '#ffcc00'};">
                {email_subject}
            </h2>
            <p>Dear Subscriber,</p>
            <p>{alert_message}</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>Volcano Information:</h3>
                <ul>
                    <li><strong>Name:</strong> {selected_volcano_name}</li>
                    <li><strong>Location:</strong> {selected_volcano.get("country", "Unknown")}</li>
                    <li><strong>Type:</strong> {selected_volcano.get("type", "Unknown")}</li>
                    <li><strong>Alert Level:</strong> {alert_level}</li>
                </ul>
            </div>
            
            <p>
                For more detailed information, please visit the 
                <a href="https://volcano-dashboard.username.repl.co">Volcano Monitoring Dashboard</a>.
            </p>
            
            <p>Stay safe!</p>
            <p>Volcano Monitoring Team</p>
            
            <div style="font-size: 12px; color: #666; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px;">
                <p>
                    This is an automated alert. Please do not reply to this email.
                    To unsubscribe or manage your alert preferences, visit the dashboard and go to the Early Warning page.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    st.markdown(email_body, unsafe_allow_html=True)


def display_subscription_plans():
    """Display available subscription plans and their features."""
    st.header("Subscription Plans")
    
    st.write("""
    Choose the subscription plan that best fits your needs. Upgrade anytime to get 
    more features and monitoring options.
    """)
    
    # Get subscription plans
    plans = get_subscription_plans()
    
    # Create columns for each plan
    columns = st.columns(len(plans))
    
    for i, plan in enumerate(plans):
        with columns[i]:
            st.subheader(plan["name"])
            st.write(f"**{plan['price']}**")
            
            for feature in plan["features"]:
                st.markdown(f"- {feature}")
            
            if plan["name"].lower() != "free":
                st.button(f"Subscribe to {plan['name']}", key=f"subscribe_{plan['name'].lower()}")
    
    st.info("""
    **Note:** This is a demonstration of a potential paid service. 
    In a real application, subscription buttons would redirect to a payment processing page.
    """)


if __name__ == "__main__":
    app()