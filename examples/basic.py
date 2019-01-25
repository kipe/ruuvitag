from ruuvitag import RuuviTag

# Run in a continuous loop
while True:
    # Run scan for available RuuviTags
    for tag in RuuviTag.scan():
        # Print information about each RuuviTag found
        print(tag)
        # Example output:
        # <RuuviTag V5 f7:bf:87:46:6f:ee 24.27c 21.59%>
