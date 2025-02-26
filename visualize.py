
import streamlit as st
import plotly.express as px
from analyze import analyze_whatsapp
import pandas as pd 

def visualize_reply_time_distributions(analyzed_data, selected_participants):
    """
    Visualizes reply time distributions using histogram, scatter plot, box plot, 
    violin plot, and average reply time bar chart.
    """

    reply_data = []
    for participant in selected_participants:
        if participant in analyzed_data["reply_time"]:
            for _, reply_time in analyzed_data["reply_time"][participant]["times"]:
                reply_data.append({"Participant": participant, "Reply Time (s)": reply_time})

    if not reply_data:
        st.warning("No reply time data available for selected participants.")
        return

    df_reply = pd.DataFrame(reply_data)

    # Histogram
    st.subheader("Histogram of Reply Time Distribution")
    fig_hist = px.histogram(df_reply, x="Reply Time (s)", color="Participant",
                             title="Reply Time Distribution Histogram")
    st.plotly_chart(fig_hist, use_container_width=True, key="hist_reply_time")

    # Scatter Plot
    st.subheader("Scatter Plot of Reply Times")
    df_reply["Index"] = range(len(df_reply))
    fig_scatter = px.scatter(df_reply, x="Index", y="Reply Time (s)", color="Participant",
                              title="Reply Times Scatter Plot")
    st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_reply_time")

    # Box Plot
    st.subheader("Box Plot of Reply Time Distribution")
    fig_box = px.box(df_reply, x="Participant", y="Reply Time (s)",
                     title="Reply Time Distribution Box Plot")
    st.plotly_chart(fig_box, use_container_width=True, key="box_reply_time")

    # Violin Plot
    st.subheader("Violin Plot of Reply Time Distribution")
    fig_violin = px.violin(df_reply, x="Participant", y="Reply Time (s)",
                           title="Reply Time Distribution Violin Plot")
    st.plotly_chart(fig_violin, use_container_width=True, key="violin_reply_time")

    # Average Reply Time Bar Chart
    st.subheader("Average Reply Time Per Participant")
    avg_reply_times = df_reply.groupby("Participant")["Reply Time (s)"].mean().reset_index()
    fig_avg_bar = px.bar(avg_reply_times, x="Participant", y="Reply Time (s)",
                          title="Average Reply Time Per Participant")
    st.plotly_chart(fig_avg_bar, use_container_width=True, key="avg_bar_reply_time")
def visualize_data(uploaded_file):
    # Read all lines from the uploaded file
    uploaded_file.seek(0)
    lines = uploaded_file.readlines()

    # Analyze chat data
    analyzed_data = analyze_whatsapp(lines)

    # Display key insights
    st.success(f"✅ **Total Messages:** {analyzed_data['total_messages']}")
    st.info(f"🕒 **First Message:** {analyzed_data['first_timestamp']}")
    st.info(f"🕒 **Last Message:** {analyzed_data['last_timestamp']}")

    # **🏅 Top 3 Frequent Chatters**
    st.subheader("🏅 Top 3 Frequent Chatters")

    sorted_chatters = sorted(analyzed_data["messages_per_person"].items(), key=lambda x: x[1], reverse=True)[:3]

    if sorted_chatters:
        col1, col2, col3 = st.columns(3)

        for idx, (name, count) in enumerate(sorted_chatters):
            emoji = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉"
            with [col1, col2, col3][idx]:
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3>{emoji} {name}</h3>
                    <p><b>{count} Messages</b></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Not enough data to determine top chatters.")

    # **Wall of Fame**
    st.subheader("🏆 Wall of Fame")

    # Finding the fastest and slowest reply time
    fastest_reply = min(analyzed_data["reply_time"].items(), key=lambda x: x[1]["fastest_reply"], default=("N/A", {"fastest_reply": "N/A"}))
    slowest_reply = max(analyzed_data["reply_time"].items(), key=lambda x: x[1]["slowest_reply"], default=("N/A", {"slowest_reply": "N/A"}))

    wall_of_fame = [
        {"Sl No.": 1, "Category": "Most Active Person", "Winner": analyzed_data["most_active_participant"], "": f'{analyzed_data["messages_per_person"][analyzed_data["most_active_participant"]]} messages'},
        # {"Sl No.": 2, "Category": "Longest Message", "Winner": analyzed_data["longest_message"]["participant"] , "": f"{analyzed_data["longest_message"]["length"]} characters"},
        {"Sl No.": 2, "Category": "Longest Message", "Winner": analyzed_data["longest_message"]["participant"] , "": f"{analyzed_data['longest_message']['length']} characters"},
        {"Sl No.": 3, "Category": "Fastest Reply Time", "Winner": fastest_reply[0], "": f"{fastest_reply[1]['fastest_reply']} Seconds"},
        {"Sl No.": 4, "Category": "Slowest Reply Time", "Winner": slowest_reply[0], "": f"{slowest_reply[1]['slowest_reply']} Seconds"},
    ]

    st.table(wall_of_fame)

    # Longest Message in the chat
    st.subheader("✉️ Longest Message")

    longest_message = analyzed_data["longest_message"]["message"]
    longest_sender = analyzed_data["longest_message"]["participant"]
    longest_length = analyzed_data["longest_message"]["length"]

    with st.expander(f"📜 {longest_sender} sent the longest message ({longest_length} characters)"):
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 10px; font-style: italic;">
            {longest_message}
        </div>
        """, unsafe_allow_html=True)

    # **Participant Selection on Main Page**
    st.subheader("👤 Filter by Participants")
    participants = analyzed_data["participants"]
    selected_participants = st.multiselect("Select Participants", participants, default=participants)

    # Filter messages per person based on selection
    filtered_messages = {p: analyzed_data["messages_per_person"].get(p, 0) for p in selected_participants}

    # Display first & last 10 messages
    first_10 = "".join([line.decode('utf-8') for line in lines[:10]])
    last_10 = "".join([line.decode('utf-8') for line in lines[-10:]])

    with st.expander("📄 First 10 Messages"):
        st.text_area("", first_10, height=200)
    
    with st.expander("📄 Last 10 Messages"):
        st.text_area("", last_10, height=200)

    # **Bar Chart** - Messages per person
    st.subheader("📊 Messages Per Participant")
    if filtered_messages:
        df = {"name": list(filtered_messages.keys()), "count": list(filtered_messages.values())}
        fig = px.bar(df, x="name", y="count", text="count", title="Message Count Per Participant")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No messages found for selected participants.")

    # **Pie Chart** - Percentage contribution
    st.subheader("📊 Message Distribution")
    if filtered_messages:
        fig_pie = px.pie(df, names="name", values="count", title="Message Contribution (%)")
        st.plotly_chart(fig_pie, use_container_width=True)


    # **Reply Time Distribution**
    st.subheader("⏳ Reply Time Distributions")
    visualize_reply_time_distributions(analyzed_data, selected_participants)

    # **Activity Timeline (Placeholder)**
    st.subheader("📅 Activity Over Time (Coming Soon!)")
    st.info("A GitHub-style heatmap for daily activity will be added later.")

    # Display all analyzed data in JSON format
    st.subheader("All Analyzed Data")
    with st.expander("Click to View JSON"):
        st.json(analyzed_data)
