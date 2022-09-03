from libinput import LibInput
li = LibInput()
device = li.path_add_device('/dev/input/event2')
li.path_remove_device(device)
print(dir(device))
for event in li.events:
    print(event)