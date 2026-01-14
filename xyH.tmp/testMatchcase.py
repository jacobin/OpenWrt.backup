def handle_command(command):
    match command:
        case "exit" | "quit" | "bye":
            print("Exiting the program.")
            # Code here runs for any of the three commands
        case "help" | "assist":
            print("Displaying help information.")
        case _:
            print(f"Unknown command: {command}")

# Example usage:
handle_command("quit")
handle_command("help")
handle_command("status")