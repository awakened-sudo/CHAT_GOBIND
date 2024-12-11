# app.py
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict
import random

# Load environment variables
load_dotenv()

class AssistantUI:
    def __init__(self):
        # Load and validate OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please ensure your .env file contains this key.")
        
        # Initialize OpenAI client with API key from .env
        self.client = OpenAI(api_key=api_key)
        
        # Hardcoded assistant and vector store IDs
        self.ASSISTANT_ID = "asst_k77pCUJSViHjAKtSMQBgnDg8"
        self.VECTOR_STORE_ID = "vs_9p6gYSeSHs3xtwK4A9yKUKNP"
        
        # Dictionary to store assistant names and IDs
        self.assistants = {
            "Honouring_Karpal_Singh": "asst_k77pCUJSViHjAKtSMQBgnDg8",
        }

        # Add translations dictionary
        self.translations = {
            "English": {
                "placeholder": "Ask your question about Minister Gobind Singh Deo...",
                "ask_button": "Ask",
                "creative_button": "I'm Feeling Creative",
                "suggested_questions": "Suggested Questions",
                "suggestions": [
                    "What are Gobind Singh Deo's key digital initiatives?",
                    "How is he transforming Malaysia's digital landscape?",
                    "What are his main technology policies?",
                    "How does he approach digital economy development?"
                ],
                "processing": "Processing your query...",
                "select_assistant": "Select Assistant",
                "start_new_conversation": "Start New Conversation"
            },
            "Bahasa Melayu": {
                "placeholder": "Tanya soalan anda tentang Menteri Gobind Singh Deo...",
                "ask_button": "Tanya",
                "creative_button": "Rasa Kreatif",
                "suggested_questions": "Soalan Dicadangkan",
                "suggestions": [
                    "Apakah inisiatif digital utama Gobind Singh Deo?",
                    "Bagaimana beliau mengubah landskap digital Malaysia?",
                    "Apakah dasar-dasar teknologi utama beliau?",
                    "Bagaimana pendekatan beliau dalam pembangunan ekonomi digital?"
                ],
                "processing": "Memproses pertanyaan anda...",
                "select_assistant": "Pilih Pembantu",
                "start_new_conversation": "Mulakan Perbualan Baru"
            },
            "عربي": {  
                "placeholder": "...اطرح سؤالك حول محتوى فيناس",
                "ask_button": "اسأل",
                "creative_button": "أشعر بالإبداع",
                "suggested_questions": "الأسئلة المقترحة",
                "suggestions": [
                    "أرني المشهد حيث يلتقي البطل مع الخصم؟",
                    "أي مشهد فيه لحظة سعيدة؟",
                    "ما هو ملخص الفيديو؟",
                    "ماذا يمكننا أن نتعلم من هذا الفيديو؟"
                ],
                "processing": "...جاري معالجة استفسارك",
                "select_assistant": "اختر مساعد",
                "start_new_conversation": "ابدأ محادثة جديدة"
            },
            "中文": {
                "placeholder": "询问有关Minister Gobind Singh Deo的问题...",
                "ask_button": "询问",
                "creative_button": "创意灵感",
                "suggested_questions": "建议问题",
                "suggestions": [
                    "Gobind Singh Deo的主要数字倡议是什么？",
                    "他如何改变马来西亚的数字景观？",
                    "他的主要技术政策是什么？",
                    "他如何处理数字经济开发？"
                ],
                "processing": "正在处理您的查询...",
                "select_assistant": "选择助手",
                "start_new_conversation": "开始新对话"
            },
            "தமிழ்": {
                "placeholder": "பிரதான அந்வர் இப்ராஹிம் பற்றி கேள்வி கேளுங்கள்...",
                "ask_button": "கேள்",
                "creative_button": "படைப்பாற்றல் உணர்கிறேன்",
                "suggested_questions": "பரிந்துரைக்கப்பட்ட கேள்விகள்",
                "suggestions": [
                    "நந்வர் இப்ராஹிம் பிரதான மாநில மேல்வாய்ப்பு என்ன?",
                    "அந்வர் குறித்து மாதிரி மலையில் எவ்வாறு வளர்ந்திருக்கிறது?",
                    "அவரின் முக்கிய நிதி நோக்கங்கள் என்ன?",
                    "அவர் விரிவாக்க வழியாக இருப்பது ���ன்ன?"
                ],
                "processing": "உங்கள் கேள்வியை செயலாக்குகிறது...",
                "select_assistant": "உதவியாளரை தேர்ந்தெடுக்கவும்",
                "start_new_conversation": "புதிய உரையாடலை தொடங்கவும்"
            }
        }

        # Add session state initialization
        if 'thread_id' not in st.session_state:
            st.session_state.thread_id = None
        if 'conversation_active' not in st.session_state:
            st.session_state.conversation_active = False

    def get_text(self, key: str, language: str) -> str:
        """Get translated text for the given key and language"""
        return self.translations[language][key]

    def get_creative_prompt(self, selected_language: str) -> str:
        """Generate creative prompts focused on video analysis and scene understanding"""
        creative_prompts = {
            "English": [
                "Analyze the emotional journey of characters throughout this scene",
                "Identify key visual storytelling techniques used in this segment",
                "Examine the scene transitions and their impact on storytelling",
                "Explore how lighting and color are used to convey mood in this scene",
                "Break down the camera movements and their narrative significance",
                "Analyze the pacing and rhythm of dialogue and action",
                "Identify symbolism and visual metaphors in this sequence",
                "Examine character dynamics and relationships in this scene"
            ],
            "Bahasa Melayu": [
                "Analisis perjalanan emosi watak dalam babak ini",
                "Kenalpasti teknik penceritaan visual dalam segmen ini",
                "Teliti peralihan babak dan kesannya terhadap penceritaan",
                "Terokai penggunaan pencahayaan dan warna untuk menyampaikan suasana",
                "Huraikan pergerakan kamera dan kepentingannya dalam naratif",
                "Analisis tempo dan ritma dialog serta aksi",
                "Kenalpasti simbolisme dan metafora visual dalam urutan ini",
                "Teliti dinamik dan hubungan antara watak dalam babak ini"
            ],
            "عربي": [
                "تحليل الرحلة العاطفية للشخصيات في هذا المشهد",
                "تحديد تقنيات السرد البصري في هذا المقطع",
                "دراسة انتقالات المشهد وتأثي��ها على السرد",
                "استكشاف استخدام الإضاءة واللون لنقل المزاج",
                "تحليل حركات الكاميرا وأهميتها السردية",
                "تحليل وتيرة وإيقاع الحوار والعمل",
                "تحديد الرمزية والاستعارات البصرية في هذا التسلسل",
                "دراسة ديناميكيات وعلاقات الشخصيات في هذا المشهد"
            ],
            "中文": [
                "分析这个场景中人物的情感变化",
                "识别此片段中使用的视觉叙事技巧",
                "研究场景转换及其对故事叙述的影响",
                "探索光线和色彩如何传达情绪",
                "分析摄像机运动及其叙事意义",
                "分析对话和动作的节奏感",
                "识别此序列中的象征主义和视觉隐喻",
                "研究这个场景中的角色互动和关系"
            ],
            "தமிழ்": [
                "இந்த காட்சியில் கதாபாத்திரங்களின் உணர்ச்சி பயணத்தை பகுப்பாய்வு செய்க",
                "இந்த பகுதியில் பயன்படுத்தப்படும் விஷுவல் கதை சொல்லும் நுட்பங்களை கண்டறியவும்",
                "காட்சி மாற்றங்களையும் கதை சொல்லலில் அவற்றின் தாக்கத்தையும் ஆராயுங்கள்",
                "மனநிலையை வெளிப்படுத்த ஒளி மற்றும் வண்ணம் பயன்படுத்தப்படும் விதத்தை ஆராயுங்கள்",
                "கேமரா அசைவுகள் மற்றும் அவற்றின் விவரிப்பு முக்கியத்துவத்தை பகுப்பாய்வு செய்யவும்",
                "உரையாடல் மற்றும் செயலின் வேகம் ம்ும் ரித்தத்தை பகுப்பாய்வு செய்யவும்",
                "இந்த வரிசையில் உள்ள சின்னங்கள் மற்றும் காட்சி உருவகங்களை கண்டறியவும்",
                "இந்த காட்சியில் கதாபாத்திர இயக்கவியல் மற்றும் உறவுகளை ஆராயவும்"
            ]
        }
            
        return random.choice(creative_prompts[selected_language])

    def initialize_assistants(self):
        """Initialize or update assistants with enforced configuration"""
        # Base instructions for all video analysis assistants
        base_instructions = """# Video Content Analysis Expert System

You are an expert video content analyst with exceptional attention to detail and precise timestamp handling. Your core responsibility is to provide comprehensive, accurate analysis of video content while maintaining absolute consistency in timestamp formatting.

## Primary Objective
Deliver precise, source-free timestamp analysis of video content that ensures all time references are clickable and functional.

## Core Rules

### Critical Timestamp Standards
- **Format**: Always use HH:MM:SS (e.g., 01:23:45)
- **Presentation**: 
  - Single point: "At [HH:MM:SS]"
  - Range: "From [HH:MM:SS] to [HH:MM:SS]"
- **Leading Format**: Begin scene descriptions with timestamps
- **Consistency**: Maintain exact format for all time references

### Absolute Prohibitions
- NO source references (†source, [source], etc.)
- NO brackets except in "At [timestamp]" format
- NO annotations or metadata with timestamps
- NO non-standard time formats

### Formatting Specifications
1. Time Components:
   - Hours: Two digits (00-23)
   - Minutes: Two digits (00-59)
   - Seconds: Two digits (00-59)

2. Presentation Rules:
   - Use 24-hour format
   - Include leading zeros
   - Maintain consistent colons
   - Preserve exact spacing

### Enhanced Clarification Protocol

#### Initial Response to Questions
1. Acknowledge query explicitly
2. Assess specificity level
3. Identify potential ambiguities
4. Structure clarification approach

#### Clarification Framework
For unclear queries, implement this structured approach:

1. **Recognition**
```
"I understand you're interested in [element]. To provide precise timestamps, I need to clarify a few points:"
```

2. **Scope Definition**
```
"Your question could encompass:
- [Specific aspect 1]
- [Specific aspect 2]
- [Specific aspect 3]

Which aspect is most relevant to your needs?"
```

3. **Precision Questions**
```
To pinpoint exact timestamps, I should know:
1. Are you interested in [specific element]?
2. Should I focus on [particular aspect]?
3. Would you prefer [option A] or [option B]?
```

4. **Context Gathering**
```
"This will help me provide:
- Exact timestamps for relevant scenes
- Appropriate context
- Connected moments if relevant"
```

### Query Categories and Response Templates

#### For Timeline Requests
```
Structure:
1. "At [HH:MM:SS]": Primary event
2. "From [HH:MM:SS] to [HH:MM:SS]": Event duration
3. Context description
4. Relevant connections
```

#### For Content Analysis
```
Format:
1. Timestamp introduction
2. Scene description
3. Technical details
4. Contextual significance
```

#### For Summary Requests
```
Organization:
1. Chronological overview with precise timestamps
2. Key moment highlighting
3. Pattern identification
4. Temporal relationships
```

### Response Quality Control

#### Pre-Submission Checklist
1. Timestamp Format Verification
   - Confirm HH:MM:SS format
   - Verify 24-hour time
   - Check leading zeros
   - Validate colon placement

2. Source Removal Verification
   - Remove all source references
   - Clear any metadata
   - Delete annotations
   - Strip brackets (except in standard format)

3. Consistency Check
   - Uniform timestamp format
   - Consistent presentation
   - Proper spacing
   - Correct sequence

## Advanced Analysis Guidelines

### Scene-by-Scene Analysis Protocol

#### Temporal Mapping
- Always lead with clean timestamp
- Maintain chronological order
- Track scene transitions
- Note temporal relationships

#### Content Elements
1. Visual Components
```
- Primary action or focus
- Key visual elements
- Technical composition
- Scene transitions
```

2. Contextual Analysis
```
- Scene significance
- Narrative progression
- Thematic elements
- Technical aspects
```

### Advanced Clarification Scenarios

#### For Complex Queries
```
Step 1: Context Assessment
"Your question about [topic] involves multiple elements. Let's break it down:
- Temporal aspects
- Content focus
- Technical elements"

Step 2: Precision Gathering
"To provide the most relevant timestamps:
1. Should we focus on [specific element]?
2. Are you interested in [particular aspect]?
3. Would you prefer [detailed aspect] or [broader view]?"

Step 3: Response Preview
"I can provide:
- Exact timestamps for each element
- Detailed scene descriptions
- Connected moments if relevant"
```

#### For Multi-Scene Analysis
```
Approach:
1. Establish primary focus
2. Identify related scenes
3. Map temporal connections
4. Build contextual bridges
```

### Response Architecture

#### Basic Response Template
```
Opening:
- Clear acknowledgment
- Scope definition
- Temporal framework

Body:
- Timestamp-led descriptions
- Contextual information
- Technical details

Conclusion:
- Summary of key points
- Related timestamps if relevant
- Optional follow-up suggestions
```

#### Advanced Response Structure
```
For Complex Analysis:
1. Primary Timeline
   - Key timestamps
   - Essential context
   - Main elements

2. Supporting Details
   - Related timestamps
   - Technical aspects
   - Contextual connections

3. Comprehensive Overview
   - Pattern identification
   - Temporal relationships
   - Thematic links
```

### Quality Assurance Protocol

#### Content Verification
1. Timestamp Accuracy
```
- Format consistency (HH:MM:SS)
- Chronological order
- Range accuracy
- Transition points
```

2. Description Quality
```
- Clear connection to timestamps
- Accurate scene details
- Relevant context
- Technical precision
```

3. Final Review Checklist
```
□ All timestamps in HH:MM:SS format
□ No source references or annotations
□ Consistent presentation
□ Logical flow
□ Clear connections
□ Accurate descriptions
```

### Special Cases Handling

#### For Technical Analysis
```
Focus Areas:
1. Equipment and setup
2. Production elements
3. Technical specifications
4. Quality indicators
```

#### For Content Patterns
```
Analysis Elements:
1. Recurring themes
2. Visual motifs
3. Technical consistencies
4. Temporal patterns
```

### Error Prevention Protocol

#### Common Pitfalls to Avoid
1. Timestamp Formatting
```
CORRECT:
- At [00:05:30]
- From [01:15:00] to [01:16:00]

INCORRECT:
- At 5:30
- From 1:15 - 1:16
- [00:05:30†source]
```

2. Response Structure
```
CORRECT:
1. Clean timestamp
2. Description
3. Context
4. Connections

INCORRECT:
1. Description
2. Timestamp with source
3. Mixed formats
```

### Final Response Verification

#### Pre-Submission Review
1. Format Check
```
- HH:MM:SS consistency
- Proper timestamp placement
- Clean presentation
- No source references
```

2. Content Review
```
- Accurate descriptions
- Clear connections
- Logical flow
- Comprehensive coverage
```

3. Quality Control
```
- Response completeness
- Information accuracy
- Format consistency
- Technical precision
```

Remember: The primary goal is to provide precise, clean timestamps with accurate content analysis while maintaining absolute consistency in format and presentation. Never include source references or annotations with timestamps."""

        # Define specific configurations for each assistant
        assistant_configs = {
            "Honouring_Karpal_Singh": {
                "name": "Honouring Karpal Singh Analyst",
                "vector_store": "vs_9p6gYSeSHs3xtwK4A9yKUKNP",
                "additional_instructions": """Focus on analyzing Minister Gobind Singh Deo's:
                    - Digital transformation initiatives
                    - Technology policies and reforms
                    - Digital economy development
                    - MDEC and digital agency oversight"""
            }
        }

        # Create or update each assistant
        for assistant_key, config in assistant_configs.items():
            complete_instructions = f"{base_instructions}\n\nSPECIFIC INSTRUCTIONS:\n{config['additional_instructions']}"
            
            # Update assistant configurations
            try:
                assistant = self.client.beta.assistants.create(
                    name=config['name'],
                    instructions=complete_instructions,
                    model="gpt-4-turbo-preview",
                    tools=[{"type": "retrieval"}],
                    metadata={"vector_store": config['vector_store']}
                )
                
                # Store the assistant ID
                self.assistants[assistant_key] = assistant.id
                
            except Exception as e:
                st.error(f"Error configuring assistant {assistant_key}: {str(e)}")


    def create_or_get_thread(self):
        """Create a new thread if none exists or return existing thread ID"""
        if not st.session_state.thread_id:
            thread = self.client.beta.threads.create()
            st.session_state.thread_id = thread.id
            
            # Add initial message as assistant instead of system
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="assistant",
                content="""IMPORTANT: I will follow these rules strictly:
                1. Always provide timestamps for every scene description
                2. Use clarification protocol for vague queries
                3. Verify all responses include proper timestamps"""
            )
            
        return st.session_state.thread_id
    
    def convert_timestamp_to_deciseconds(self, timestamp_str):
        """Convert HH:MM:SS timestamp to deciseconds"""
        try:
            # Handle different timestamp formats
            if ":" in timestamp_str:
                parts = timestamp_str.split(":")
                if len(parts) == 3:  # HH:MM:SS
                    h, m, s = map(float, parts)
                    total_seconds = h * 3600 + m * 60 + s
                elif len(parts) == 2:  # MM:SS
                    m, s = map(float, parts)
                    total_seconds = m * 60 + s
                else:
                    return None
                # Convert to deciseconds for more precise timing
                return int(total_seconds * 10)  # Multiply by 10 for deciseconds
            return None
        except:
            return None

    def create_timestamp_link(self, match, file_id):
        """Create clickable link for timestamp with decisecond precision"""
        timestamp = match.group(0)
        deciseconds = self.convert_timestamp_to_deciseconds(timestamp)
        if deciseconds is not None:
            # Add decisecond precision to URL
            return f'<a href="https://finas.ortana.tv/Clips/View?FleId={file_id}&offset={deciseconds/10}" target="_blank">{timestamp}</a>'
        return timestamp

    def process_message_content(self, content, file_id):
        """Process message content to add timestamp links"""
        import re
        
        # Enhanced pattern to match more timestamp formats
        timestamp_pattern = r'\b\d{1,2}:\d{2}(:\d{2})?(\.\d{1,3})?\b'
        
        # Replace timestamps with clickable links
        processed_content = re.sub(
            timestamp_pattern,
            lambda m: self.create_timestamp_link(m, file_id),
            content
        )
        
        return processed_content

    def run(self):
        # Set page config and title
        st.set_page_config(page_title="RAMP-AI by BlacX", layout="centered")
        
        # Custom CSS for Google-like styling
        st.markdown("""
            <style>
            .big-font {
                font-size:50px !important;
                font-weight:bold;
                text-align:center;
                margin-bottom:30px;
                background: linear-gradient(45deg, #1e3c72, #2a5298);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .search-box {
                border-radius:24px !important;
                border:1px solid #dfe1e5 !important;
                padding:10px 20px !important;
                width:100% !important;
                margin:20px 0 !important;
            }
            .stButton button {
                background-color:#f8f9fa;
                border:1px solid #f8f9fa;
                border-radius:4px;
                color:#3c4043;
                margin:11px 4px;
                padding:0 16px;
                height:36px;
                cursor:pointer;
            }
            .stButton button:hover {
                border:1px solid #dadce0;
                box-shadow:0 1px 1px rgba(0,0,0,.1);
            }
            
            /* Add RTL support for Arabic */
            [lang="ar"] {
                direction: rtl;
                text-align: right;
                font-family: 'Arial', sans-serif;
            }
            
            /* Adjust input fields for RTL when Arabic is selected */
            .rtl-support {
                direction: rtl;
                text-align: right;
            }

        
            
            .assistant-info {
                font-size: 0.9em;
                color: #666;
                margin-top: 5px;
            }
            </style>
            <div class="big-font">RAMP-AI by BlacX</div>
        """, unsafe_allow_html=True)
        
        # Language selector and "New Conversation" button side by side
        languages = list(self.translations.keys())
        col_lang, col_button = st.columns([3, 1])
        
        with col_lang:
            selected_language = st.selectbox(
                "Select Language",
                languages,
                label_visibility="collapsed"
            )
        
        with col_button:
            if st.session_state.conversation_active:
                if st.button(self.get_text("start_new_conversation", selected_language)):
                    st.session_state.thread_id = None
                    st.session_state.conversation_active = False
                    st.rerun()

        # Add assistant selector with description
        st.markdown("<div class='assistant-selector'>", unsafe_allow_html=True)

        # Define assistant IDs and their corresponding vector stores
        assistant_vector_stores = {
            "Honouring_Karpal_Singh": "vs_9p6gYSeSHs3xtwK4A9yKUKNP"
        }

        # Initialize session state for tracking assistant changes
        if "current_assistant" not in st.session_state:
            st.session_state.current_assistant = list(self.assistants.keys())[0]
            st.session_state.current_vector_store = assistant_vector_stores[st.session_state.current_assistant]

        def switch_assistant():
            # Update assistant and vector store IDs
            st.session_state.current_assistant = selected_assistant_name
            st.session_state.current_vector_store = assistant_vector_stores[selected_assistant_name]
            
            # Log the changes using os.write for console output
            import os
            os.write(1, f"\nSwitching Assistant:".encode())
            os.write(1, f"\nAssistant ID: {self.assistants[selected_assistant_name]}".encode())
            os.write(1, f"\nVector Store ID: {assistant_vector_stores[selected_assistant_name]}\n".encode())
            
            # Clear conversation state
            st.session_state.thread_id = None
            st.session_state.conversation_active = False

        # Add assistant selector
        selected_assistant_name = st.selectbox(
            self.get_text("select_assistant", selected_language),
            list(self.assistants.keys()),
            format_func=lambda x: f"🤖 {x}",
            key="assistant_selector"
        )

        # Add switch button with callback
        if st.button("Switch Assistant", 
                    on_click=switch_assistant,
                    type="primary"):
            # The callback function will handle the state updates
            st.rerun()

        # Update the assistant ID and vector store ID from session state
        self.ASSISTANT_ID = self.assistants[st.session_state.current_assistant]
        self.VECTOR_STORE_ID = st.session_state.current_vector_store

        # Update assistant description display
        assistant_descriptions = {
            "Honouring_Karpal_Singh": "link here",
        }
        st.markdown(f"<div class='assistant-info'>{assistant_descriptions.get(selected_assistant_name, '')}</div>", 
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Use translated text throughout the interface
        rtl_class = "rtl-support" if selected_language == "عربي" else ""
        query = st.text_input(
            "Search",
            placeholder=self.get_text("placeholder", selected_language),
            label_visibility="collapsed",
            key="search_box",
            kwargs={
                "class": rtl_class,
                "dir": "rtl" if selected_language == "عربي" else "ltr"
            }
        )
        
        # Buttons with translations
        col1, col2 = st.columns([1, 1])
        with col1:
            search = st.button(
                self.get_text("ask_button", selected_language), 
                use_container_width=True
            )
        with col2:
            lucky = st.button(
                self.get_text("creative_button", selected_language), 
                use_container_width=True
            )
        
        # Suggested questions with translations
        st.markdown(f"### {self.get_text('suggested_questions', selected_language)}")
        suggestions = self.get_text("suggestions", selected_language)
        
        # Display suggestions in a grid
        cols = st.columns(2)
        for idx, suggestion in enumerate(suggestions):
            with cols[idx % 2]:
                if st.button(suggestion, key=f"sug_{idx}", use_container_width=True):
                    query = suggestion
                    search = True

        
        # Handle search with translated processing message
        if search or lucky:
            st.markdown("---")
            with st.spinner(self.get_text("processing", selected_language)):
                try:
                    # Get or create thread
                    thread_id = self.create_or_get_thread()
                    
                    # Determine the content to send
                    if lucky:  # I'm Feeling Creative button
                        if not query:  # If no query entered, use a random creative prompt
                            query = self.get_creative_prompt(selected_language)
                            st.info(f"Creative Prompt: {query}")
                        else:  # If query exists, enhance it creatively
                            creative_query = f"Please provide a creative and innovative response about: {query}. Think outside the box and suggest unique perspectives or possibilities while staying within FINAS guidelines."
                            query = creative_query

                    # Add message to thread
                    message = self.client.beta.threads.messages.create(
                        thread_id=thread_id,
                        role="user",
                        content=f"[Language: {selected_language}] {query}"
                    )
                    
                    # Create and run assistant
                    run = self.client.beta.threads.runs.create(
                        thread_id=thread_id,
                        assistant_id=self.ASSISTANT_ID,
                        additional_instructions=f"Use vector store {assistant_vector_stores[selected_assistant_name]} for {selected_assistant_name}"
                    )
                    
                    # Wait for completion
                    while True:
                        run_status = self.client.beta.threads.runs.retrieve(
                            thread_id=thread_id,
                            run_id=run.id
                        )
                        if run_status.status == 'completed':
                            break
                        elif run_status.status in ['failed', 'cancelled', 'expired']:
                            st.error(f"Run failed with status: {run_status.status}")
                            return
                    
                    # Get all messages in the thread
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread_id
                    )
                    
                    # Get file_id based on selected assistant
                    file_ids = {
                        "Honouring_Karpal_Singh": "855112"
                    }
                    file_id = file_ids.get(selected_assistant_name)
                    
                    # Display conversation history
                    st.markdown("### Conversation:")
                    for msg in messages.data:
                        role = "🧑" if msg.role == "user" else "🤖"
                        for content in msg.content:
                            if content.type == 'text':
                                # Process content to add timestamp links
                                processed_content = self.process_message_content(
                                    content.text.value,
                                    file_id
                                )
                                
                                st.markdown(f"""
                                <div style='background-color:{"#f0f2f6" if msg.role == "user" else "#f8f9fa"}; 
                                         padding:20px; 
                                         border-radius:10px;
                                         margin: 5px 0;'>
                                    <strong>{role}</strong>: {processed_content}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Mark conversation as active
                    st.session_state.conversation_active = True

                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")

if __name__ == "__main__":
    app = AssistantUI()
    app.run()