import streamlit as st
from leafmap.foliumap import Map
import os
import requests
from map_helpers import mark_llm_places
from geo_helpers import get_ndvi_value, get_lst_value, all_regions, patch_placeholders
from datetime import datetime
import json
import re

# ---------- CONFIG ---------- #
st.set_page_config(layout="wide")

# ---------- SESSION STATE INIT ---------- #
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'map_center' not in st.session_state:
    st.session_state.map_center = [19.07, 72.87]
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 10

# ---------- LLM QUERY FUNCTION with FOLLOW-UP MEMORY ---------- #
def query_llm(prompt, chat_history):
    past_turns = ""
    for chat in chat_history[-4:]:
        past_turns += f"\nUser: {chat['user']}\nAssistant: {chat['llm']}"

    full_prompt = f"""
You are Geo-LLM, a smart assistant that helps with geospatial heatwave analysis for Mumbai using satellite data (NDVI, LST, vegetation, risk zones etc.).

You have access to datasets collected in the local data folder (e.g. LST 2022, NDVI 2023) and tools that can extract values from them.

You should:
1. Think step-by-step (3 short bullet points)
2. Give a final conclusion
3. If a user asks follow-up queries, refer to the past context
4. If the user asks something unrelated to Mumbai or heatwaves, politely decline

Use the following format:
Step 1: ...
Step 2: ...
Step 3: ...
=> Final Answer: ...

Conversation so far:
{past_turns}

User: {prompt}
Assistant:"""

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral",
        "prompt": full_prompt,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        return result.get("response", "")
    except Exception as e:
        return f"❌ Error querying LLM: {e}"

# ---------- VALIDITY FILTER ---------- #
def is_valid_query(text):
    if not text.strip():
        return False

    if st.session_state.get("chat_history"):
        return True

    heat_keywords = ["heat", "temperature", "lst", "ndvi", "vegetation", "risk", "urban", "green", "dry", "hot"]
    location_keywords = all_regions

    text = text.lower()
    has_heat_term = any(word in text for word in heat_keywords)
    has_region = any(loc in text for loc in location_keywords)

    return has_heat_term and has_region

# ---------- SAVE MAP OUTPUT ---------- #
def save_map_output(query, layer, answer):
    if 'saved_maps' not in st.session_state:
        st.session_state['saved_maps'] = []
    st.session_state['saved_maps'].append({
        "query": query,
        "layer": layer,
        "llm_answer": answer,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    with open("saved_maps.json", "w") as f:
        json.dump(st.session_state['saved_maps'], f)

# ---------- HEADER ---------- #
col1, col2 = st.columns([6, 2])
with col1:
    st.markdown("""
    <h1 style='color:white; background-color:#111; padding:20px 30px; border-radius:10px; font-size:48px;'>Geo-LLM</h1>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style='text-align:right; padding-top:20px;'>
        <button style='margin: 5px; padding: 10px 18px; border-radius: 10px; background-color: #e65c1c; color: white; border: none;'>sign up</button>
        <button style='margin: 5px; padding: 10px 18px; border-radius: 10px; background-color: #e65c1c; color: white; border: none;'>log in</button>
    </div>
    """, unsafe_allow_html=True)

# ---------- SIDEBAR ---------- #
st.sidebar.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #c23d00;
    color: white;
}
.sidebar-option {
    padding: 10px;
    border-bottom: 1px solid #fff;
    font-size: 16px;
}
</style>
<div class='sidebar-option'>☰</div>
<div class='sidebar-option'>Dashboard</div>
<div class='sidebar-option'>History</div>
<div class='sidebar-option'>Saved Maps</div>
<div class='sidebar-option'>Deleted</div>
<div class='sidebar-option'>Log Out</div>
""", unsafe_allow_html=True)

# ---------- LAYER SELECT ---------- #
selected_layer = st.sidebar.radio("Select a Heatmap Layer:", ["LST 2022", "NDVI 2023", "Risk Map"])
m = Map(center=st.session_state.map_center, zoom=st.session_state.zoom_level)
st.session_state.map_obj = m

# ---------- CHAT HISTORY ---------- #
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(chat['user'])
        with st.chat_message("assistant"):
            if "=>" in chat['llm']:
                reasoning, final = chat['llm'].split("=>", 1)
                st.markdown("**🧠 Reasoning:**")
                for line in reasoning.strip().split("\n"):
                    st.markdown(f"- {line.strip()}")
                st.markdown("**✅ Final Answer:**")
                st.success(final.strip())
            else:
                st.markdown(chat['llm'])

# ---------- USER QUERY ---------- #
user_query = st.chat_input("Ask your geospatial question related to heatwave in Mumbai:")
if user_query:
    if is_valid_query(user_query):
        with st.spinner("Geo-LLM is thinking..."):
            llm_response = query_llm(user_query, st.session_state.chat_history)
            patched_response, zoom_coords = patch_placeholders(llm_response)
            st.session_state.chat_history.append({"user": user_query, "llm": patched_response})
            save_map_output(user_query, selected_layer, patched_response)

            with st.chat_message("user"):
                st.markdown(user_query)
            with st.chat_message("assistant"):
                if "=>" in patched_response:
                    reasoning, final = patched_response.split("=>", 1)
                    st.markdown("**🧠 Reasoning:**")
                    for line in reasoning.strip().split("\n"):
                        st.markdown(f"- {line.strip()}")
                        zoom = mark_llm_places(line, m)
                        if zoom:
                            st.session_state.map_center = zoom
                            st.session_state.zoom_level = 13
                    st.markdown("**✅ Final Answer:**")
                    st.success(final.strip())
                else:
                    st.markdown(patched_response)

            region_match = re.search(r"(" + "|".join(all_regions) + ")", user_query.lower())
            if region_match:
                region_name = region_match.group(1)

                ndvi_val = get_ndvi_value(region_name)
                lst_val = get_lst_value(region_name)

                if ndvi_val is not None:
                    st.markdown(f"🌿 **NDVI for {region_name.title()}**: `{ndvi_val}`")

                if lst_val is not None:
                    st.markdown(f"🌡️ **LST for {region_name.title()}**: `{lst_val}°C`")
    else:
        st.warning("❌ Only Mumbai heatwave-related queries allowed.")

# ---------- MAP LAYERS ---------- #
if selected_layer == "LST 2022":
    path = "data/gee/lst_series/lst_2022.tif"
    if os.path.exists(path):
        m.add_raster(path, layer_name="LST 2022", colormap="inferno", opacity=0.5)
        m.add_legend(title="LST (°C)",
                     colors=["#000004", "#420A68", "#932667", "#DD513A", "#FCA50A", "#FCFFA4"],
                     labels=["<20°C", "25°C", "30°C", "35°C", "40°C", "45°C+"],
                     position="bottomright")
elif selected_layer == "NDVI 2023":
    path = "data/gee/yearly_ndvi_2023.tif"
    if os.path.exists(path):
        m.add_raster(path, layer_name="NDVI", colormap="YlGn", opacity=0.6)
        m.add_legend(title="NDVI", colors=["#f7fcf5", "#c7e9c0", "#74c476", "#238b45", "#00441b"],
                     labels=["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"], position="bottomright")
elif selected_layer == "Risk Map":
    path = "processed/risk_layer.tif"
    if os.path.exists(path):
        m.add_raster(path, layer_name="Risk", colormap="Reds", opacity=0.6)
        m.add_legend(title="Risk", colors=["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],
                     labels=["Very Low", "Low", "Moderate", "High", "Very High"], position="bottomright")

# ---------- RENDER MAP ---------- #
m.to_streamlit(height=700)
