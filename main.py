import asyncio, websockets, threading, colorama, time

async def hello(localclient):
    global client_id, exiting
    async with websockets.connect(REMOTE_URL) as remote:
        client_id = None
        print("Connected! Enter digits of hacks to toggle:")
        
        taskA = asyncio.create_task(clientToServer(remote, localclient))
        taskB = asyncio.create_task(serverToClient(remote, localclient))
        input_thread = threading.Thread(target=toggler, args=(hacks_enabled,))
        input_thread.start()

        await taskA
        await taskB

def toggler(hacks_enabled):
    global deinit_yourself, deinit_yourself_2, exiting
    deinit_yourself = False
    deinit_yourself_2 = False
    colorama.init(autoreset=True)
    while True:
        prefixes = {}
        for i in range(1, 10):
            try:
                if hacks_enabled[i]:
                    prefixes[i] = colorama.Fore.GREEN + str(i) + ". "
                else:
                    prefixes[i] = colorama.Fore.RED + str(i) + ". "
            except:
                prefixes[i] = colorama.Fore.RED + str(i) + ". "
        print("\n\n\n\n\n\n")
        print(prefixes[1] + "Nerf Anti-Cheat - prevents you from sending some forbidden packets") # done
        print(prefixes[2] + "Invisibility - hides your cursor") # done
        print(prefixes[3] + "Multiplayern't - hides everyone's cursors") # done
        print(prefixes[4] + "Cleaner - will replace all incoming cells with void (aka forcing erase mode for everyone)") # done
        print(prefixes[5] + "Force Sandbox Mode - switches you to sandbox mode while level mode is active") # done
        print(prefixes[6] + "Printer - prints all sent and recieved packets") # done
        print(prefixes[7] + "Show Yourself - allows you to see your own cursor") # done
        print(prefixes[8] + "Hover Flex - shows your last placed cell as a hover on your cursor") # done
        print(prefixes[9] + "No Wrap - stops all wrap packets from both sides (aka your wrap mode becomes fully local)") # done
        print('"exit" to exit')
        
        try:
            hack = input("Toggle: ")
            hack = int(hack)
            try:
                hacks_enabled[hack] = not hacks_enabled[hack]
                if hacks_enabled[hack] == False and hack == 7:
                    deinit_yourself = True
                if hacks_enabled[hack] == False and hack == 8:
                    deinit_yourself_2 = True
            except:
                hacks_enabled[hack] = True
        except:
            if hack == "exit":
                exiting = True
                print("Abyss will close on next packet.")
                break
            else:
                print("Invalid hack!")

def is_hack(value):
    global hacks_enabled
    try:
        return hacks_enabled[value]
    except:
        hacks_enabled[value] = False
        return hacks_enabled[value]

async def serverToClient(remote, localclient):
    global hacks_enabled, client_id, cellid, exiting, hovering_name
    hovering_name = ""
    async for message in localclient:
        if exiting:
            await remote.close()
            await localclient.close()
            break
        do_send = True
        if message.startswith("set-cursor") and client_id == None:
            stuff = message.split(" ")
            client_id = stuff[1]
        if (is_hack(2) or is_hack(3)) and message.startswith("set-cursor") and message.split(" ")[1] == client_id:
            message = "set-cursor " + client_id + " 69420.87006875000003 69420.13745000000001"
        if is_hack(4) and message.startswith("place"):
            x = message.split(" ")[1]
            y = message.split(" ")[2]
            message = f"place {x} {y} empty 0 0"
        if is_hack(8) and message.startswith("place"):
            x = message.split(" ")[1]
            y = message.split(" ")[2]
            cellid = message.split(" ")[3]
            new_message = f"new-hover {client_id} {x} {y} {cellid} 0"
            await remote.send(new_message)
            
            hovering_name_temp = "YouAreHolding" + cellid[0].upper() + cellid[1:]
            if hovering_name != hovering_name_temp:
                await localclient.send(f"set-cursor {hovering_name} 69420.87006875000003 69420.13745000000001")
            hovering_name = hovering_name_temp
            new_message = f"set-cursor {hovering_name} {x} {y}"
            await localclient.send(new_message)
        if is_hack(1) and (message.startswith("edtype") or message.startswith("remove-cursor")):
            do_send = False
        if is_hack(9) and message.startswith("wrap"):
            do_send = False
            await localclient.send("wrap") # apperantly i need to send it back to myself
        
        if do_send:
            if is_hack(6):
                print("> " + message)
            await remote.send(message)
    raise KeyboardInterrupt

async def clientToServer(remote, localclient):
    global client_id, deinit_yourself, deinit_yourself_2, hovering_name
    async for message in remote:
        if deinit_yourself and message.startswith("set-cursor") and message.split(" ")[1] == client_id:
            deinit_yourself = False
            name = message.split(" ")[1] + "_"
            new_message = f"set-cursor {name} 69420.87006875000003 69420.13745000000001"
            await localclient.send(new_message)
        if deinit_yourself_2 and message.startswith("set-cursor") and message.split(" ")[1] == client_id:
            deinit_yourself_2 = False
            name = message.split(" ")[1] + "_"
            new_message = f"set-cursor {hovering_name} 69420.87006875000003 69420.13745000000001"
            await localclient.send(new_message)
            new_message = "drop-hover " + client_id
            await remote.send(new_message)
        if is_hack(3) and message.startswith("set-cursor"):
            new_message = "set-cursor " + message.split(" ")[1] + " 69420.87006875000003 69420.13745000000001"
            if is_hack(6):
                print("> " + message)
            await remote.send(new_message)
        if is_hack(5):
            await localclient.send("edtype sandbox")
            hacks_enabled[5] = False
        if is_hack(4) and message.startswith("place"):
            x = message.split(" ")[1]
            y = message.split(" ")[2]
            new_message = f"place {x} {y} empty 0 0"
            if is_hack(6):
                print("> " + new_message)
            await remote.send(new_message)
        if is_hack(7) and message.startswith("set-cursor") and message.split(" ")[1] == client_id:
            name = message.split(" ")[1] + "_"
            x = message.split(" ")[2]
            y = message.split(" ")[3]
            new_message = f"set-cursor {name} {x} {y}"
            await localclient.send(new_message)
        if is_hack(9) and message.startswith("wrap"):
            continue # wow very complicated hack
            
        if is_hack(6):
            print("< " + message)
        await localclient.send(message)

async def main():
    global exiting
    async with websockets.serve(hello, "localhost", 6969):
        print("Started proxy! Connect to 127.0.0.1:6969 in your TPC to start...")
        if not exiting:
            await asyncio.Future()  # run forever

if __name__ == "__main__":
    exiting = False
    print("Welcome to Abyss for TPC by Milenakos#3310!")
    REMOTE_URL = input("Enter server you want to connect to: ")
    hacks_enabled = {}
    if "repl.co" in REMOTE_URL and not REMOTE_URL.startswith("ws"):
        REMOTE_URL = "wss://" + REMOTE_URL
    elif not REMOTE_URL.startswith("ws"):
        REMOTE_URL = "ws://" + REMOTE_URL
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Goodbye!")