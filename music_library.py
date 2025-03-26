from colorama import Fore, Style

class Members:
    def __init__(self):
        self.members = set()

    def check_admin_credentials(self):
        user = "admin"
        password = "admin"
        credentials = input(Fore.GREEN + "Enter credentials: " + Style.RESET_ALL)
        if credentials == f"{user}:{password}":
            return True
        else:
            return False
        
    def main_menu(self):
        print(Fore.GREEN + "1. Admin" + Style.RESET_ALL)
        print(Fore.GREEN + "2. User" + Style.RESET_ALL)
        print(Fore.GREEN + "3. Exit" + Style.RESET_ALL)

        ask = input(Fore.GREEN + "Enter choice: " + Style.RESET_ALL)
        if ask == "1" or ask == "Admin":
            self.display_admin_menu()
        elif ask == "2" or ask == "User":
            self.check_member()
        elif ask == "3" or ask == "Exit":
            print(Fore.GREEN + "Exiting..." + Style.RESET_ALL)
            exit()
        else:
            print(Fore.RED + "Invalid choice" + Style.RESET_ALL)
            self.main_menu()

    def display_admin_menu(self):
        if self.check_admin_credentials():
            print(Fore.GREEN + "1. Add member" + Style.RESET_ALL)
            print(Fore.GREEN + "2. Remove member" + Style.RESET_ALL)
            print(Fore.GREEN + "3. Display members" + Style.RESET_ALL)
            print(Fore.GREEN + "4. Exit" + Style.RESET_ALL)

            ask = input(Fore.GREEN + "Enter choice: " + Style.RESET_ALL)
            if ask == "1":
                self.add_member()
            elif ask == "2":
                self.remove_member()
            elif ask == "3":
                self.display_members()
            elif ask == "4":
                self.main_menu()
        else:
            print(Fore.RED + "Invalid credentials" + Style.RESET_ALL)
            self.main_menu()

    def add_member(self):
        name = input(Fore.GREEN + "Enter name: " + Style.RESET_ALL)
        age = input(Fore.GREEN + "Enter age: " + Style.RESET_ALL)
        with open("members.txt", "a") as file:
            file.write(f"{name}:{age}\n")
        self.members.add((name, age))

    def remove_member(self):
        name = input(Fore.GREEN + "Enter name: " + Style.RESET_ALL)
        age = input(Fore.GREEN + "Enter age: " + Style.RESET_ALL)
        self.members.discard((name, age))
    
    def display_members(self):
        with open("members.txt", "r") as file:  
            members = [x.strip() for x in file.readlines()]
            print(Fore.GREEN + "Members: " + Style.RESET_ALL + ', '.join(map(str, members)))
        
        if len(members) == 0:
            print(f"{Fore.WHITE}Members: {Fore.RED}Empty{Style.RESET_ALL}")

    def check_member(self):
        name = input(Fore.GREEN + "Enter name: " + Style.RESET_ALL)
        age = input(Fore.GREEN + "Enter age: " + Style.RESET_ALL)
        with open("members.txt", "r") as file:
            for line in file:
                display_members = line.strip().split(":")
                name_display = display_members[0]
                age_display = display_members[1]
                if (name, age) == (name_display, age_display):
                    print(Fore.GREEN + "Member found" + Style.RESET_ALL)
                    music_library.display_menu()
                    return True
                else:
                    print(Fore.RED + "Member not found" + Style.RESET_ALL)
            return False

class MusicLibrary:
    def __init__(self, hiphop_library, rock_library, pop_library):
        self.hiphop_library = hiphop_library
        self.rock_library = rock_library
        self.pop_library = pop_library

    def display_menu(self):
        print(Fore.GREEN + "1. Add song" + Style.RESET_ALL)
        print(Fore.GREEN + "2. Remove song" + Style.RESET_ALL)
        print(Fore.GREEN + "3. Display library" + Style.RESET_ALL)
        print(Fore.GREEN + "4. Exit" + Style.RESET_ALL)

        ask = input(Fore.GREEN + "Enter choice: " + Style.RESET_ALL)
        if ask == "1":
            genre = input(Fore.GREEN + "Enter genre: " + Style.RESET_ALL)
            self.add_song(genre)
            self.display_menu()
        elif ask == "2":
            genre = input(Fore.GREEN + "Enter genre: " + Style.RESET_ALL)
            self.remove_song(genre)
            self.display_menu()
        elif ask == "3":
            self.display_entire_library()
            self.display_menu()
        elif ask == "4":
            print(Fore.GREEN + "Exiting..." + Style.RESET_ALL)
            exit()
        else:
            print(Fore.RED + "Invalid choice" + Style.RESET_ALL)
            self.display_menu()
            
    def display_entire_library(self):
        ask = input(Fore.GREEN + "Display entire library? (y/n): " + Style.RESET_ALL)
        if ask == "y":
            if len(self.hiphop_library) == 0 and len(self.rock_library) == 0 and len(self.pop_library) == 0:
                print(f"{Fore.WHITE}Library: {Fore.RED}Empty{Style.RESET_ALL}")
            else:
                print(Fore.GREEN + "Hip-Hop Library: " + Style.RESET_ALL + ', '.join(map(str, self.hiphop_library)))
                print(Fore.GREEN + "Rock Library: " + Style.RESET_ALL + ', '.join(map(str, self.rock_library)))
                print(Fore.GREEN + "Pop Library: " + Style.RESET_ALL + ', '.join(map(str, self.pop_library)))
        elif ask == "n":
            genre = input(Fore.GREEN + "Enter genre: " + Style.RESET_ALL)
            self.display_library(genre)
        else:
            print(Fore.RED + "Invalid choice" + Style.RESET_ALL)

    def add_song(self, genre):
        song = input(Fore.GREEN + "Enter song to add: " + Style.RESET_ALL)
        if genre == "hiphop":
            with open("hiphop_library.txt", "r") as file:
                songs = [x.strip() for x in file.readlines()]        
            if song in songs:
                print(Fore.RED + "Song already exists" + Style.RESET_ALL)
                self.display_menu()
            else:
                with open("hiphop_library.txt", "a") as file:
                    file.write(f"{song}\n")
                self.hiphop_library.append(song)
                self.display_menu()
        elif genre == "rock":
            with open("rock_library.txt", "r") as file:
                songs = [x.strip() for x in file.readlines()] 
            if song in songs:
                print(Fore.RED + "Song already exists" + Style.RESET_ALL)
                self.display_menu()
            else:
                with open("rock_library.txt", "a") as file:
                    file.write(f"{song}\n")
                self.rock_library.append(song)
                self.display_menu()
        elif genre == "pop":
            with open("pop_library.txt", "r") as file:
                songs = [x.strip() for x in file.readlines()]
            if song in songs:
                print(Fore.RED + "Song already exists" + Style.RESET_ALL)
                self.display_menu()
            else:
                with open("pop_library.txt", "a") as file:
                    file.write(f"{song}\n")
                self.pop_library.append(song)
                self.display_menu()
        else:
            print(Fore.RED + "Invalid genre" + Style.RESET_ALL)
            self.display_menu()
    
    def remove_song(self, genre):
        song = input(Fore.GREEN + "Enter song to remove: " + Style.RESET_ALL)
        if genre == "hiphop":
            if song in self.hiphop_library:
                self.hiphop_library.remove(song)
                self.display_menu()
            else:
                print(Fore.RED + "Song not found" + Style.RESET_ALL)
                self.display_menu()
        elif genre == "rock":
            if song in self.rock_library:
                self.rock_library.remove(song)
                self.display_menu()
            else:
                print(Fore.RED + "Song not found" + Style.RESET_ALL)
                self.display_menu()
        elif genre == "pop":
            if song in self.pop_library:
                self.pop_library.remove(song)
                self.display_menu()
            else:
                print(Fore.RED + "Song not found" + Style.RESET_ALL)
                self.display_menu()
        else:
            print(Fore.RED + "Invalid genre" + Style.RESET_ALL)
            self.display_menu()

    def display_library(self, genre):
        if genre == "hiphop":
            if len(self.hiphop_library) == 0:
                print(f"{Fore.WHITE}Hip-Hop Library: {Fore.RED}Empty{Style.RESET_ALL}")
                self.display_menu()
            else:
                print(Fore.GREEN + "Hip-Hop Library: " + Style.RESET_ALL + ', '.join(map(str, self.hiphop_library)))
                self.display_menu()
        elif genre == "rock":
            if len(self.rock_library) == 0:
                print(f"{Fore.WHITE}Rock Library: {Fore.RED}Empty{Style.RESET_ALL}")
                self.display_menu()
            else:
                print(Fore.GREEN + "Rock Library: " + Style.RESET_ALL + ', '.join(map(str, self.rock_library)))
                self.display_menu()
        elif genre == "pop":
            if len(self.pop_library) == 0:
                print(f"{Fore.WHITE}Pop Library: {Fore.RED}Empty{Style.RESET_ALL}")
                self.display_menu()
            else:
                print(Fore.GREEN + "Pop Library: " + Style.RESET_ALL + ', '.join(map(str, self.pop_library)))
                self.display_menu()
        else:
            print(Fore.RED + "Invalid genre" + Style.RESET_ALL)
            self.display_menu()

if __name__ == "__main__":
    hiphop_library = []
    rock_library = []
    pop_library = []
    members = Members()
    music_library = MusicLibrary(hiphop_library, rock_library, pop_library)
    while True:
        members.main_menu()