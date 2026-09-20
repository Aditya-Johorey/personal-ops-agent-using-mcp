from memory import add_memory, search_memory

if __name__ == "__main__":
    add_memory(
        user_message="I usually prefer meetings in the afternoon, not mornings.",
        assistant_message="Got it, I'll keep that in mind for scheduling.",
    )
    print("Memory added.")

    results = search_memory("What time of day does the user prefer meetings?")
    print("Relevant memories found:")
    for r in results:
        print(" -", r)