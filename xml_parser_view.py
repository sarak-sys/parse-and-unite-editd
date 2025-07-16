import tkinter as tk
from tkinter import ttk
import os
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import re
from utils.xml_parser_model import Model
from utils.united import United
from utils.outpsm import xlsx_outpsm
import platform
import subprocess

MAIN_FONT = ("Arial Bold", 10)


class Controller(tk.Tk):
    """
    creates two graphic pages- one is unused at the moment! so only "StartPage"
    communicates with Model- the actual parser

    """
    def __init__(self):
        self.model = Model()            # the actual parser
        self.files: list = list()       # all pep-xml files to parse and unite
        self.file_names = list()         # the filenames after manipulation by func "update file names"
        self.swap_dict = dict()         # key: name of file value: 0 if light/heavy and 1 if heavy/light
        self.dict_list = list()         # all files AFTER parsing
        self.number_of_files = 0
        self.curr_dir = ""
        tk.Tk.__init__(self)
        #   cat icon misbehaving in linux
        # tk.Tk.iconbitmap(self, default="catIcon.ico")
        self.error_rate_button = tk.StringVar()     # 0/ 0.01 / 0.005 / 0.001
        self.running_options = tk.StringVar()       # "default" "label" or "lysine"
        self.output_entry = ""  # name of united file output. to use it - "self.output_entry.get()"
        # self.label_free = tk.IntVar()   # if 1 than consider
        self._initialize_radio_buttons()
        self.title("PEP-XML PARSER")
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames: dict = {}
        frame = StartPage(self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def _update_file_names(self):
        """
        creating output file in current running directory- output_entry.get()+file_numbers.txt

        1 - first file name
        2 - second file name
        ...
        also print it in terminal

        """
        #try:
            # print(str(self.output_entry.get()))
        self.curr_dir = os.path.split(self.files[0])[0]
        self.curr_dir = self.curr_dir + "/"
        self.model.curr_dir = self.curr_dir
        #print(self.model.curr_dir)
        file_numbers = open(self.curr_dir + str(self.output_entry.get()) +"_file_numbers.txt", "w")
        for i, f in zip(range(self.number_of_files), self.files):
                # remove the pathname and the .xml of the file name string

                base = os.path.basename(f)  # remove path name
                base = os.path.splitext(base)   # remove .xmk
                base = base[0]  # take only the name. no need of .xml
                if base.startswith('interact-'):    # if the filename start with "interact-" then remove it
                    base = re.sub('interact-', '', base)
                if base.endswith('.pep'):           # if filename end with "."pep" remove it
                    base = re.sub('\.pep$', '', base)
                self.file_names.append(base)
                #print(str(i+1) + "   " + str(base))
                file_numbers.write(str(i+1) + "   " + str(f) + "\n")
        file_numbers.close()
        #print (self.file_names)

        #except:
         #   self.error_message("Invalid file", "Cannot parse\n file_numbers.txt in use")
          #  os._exit(1)

    def _initialize_radio_buttons(self):
        # self.label_free.set(0)
        self.running_options.set("-1")
        self.error_rate_button.set("-1")

    def choose_file(self):
        self.files = self.frames[StartPage].browse()
        self.number_of_files = len(self.files)
        validation = self.model.validation(self.files, self.number_of_files)
        if validation == "Exit":
            self.frames[StartPage].change_number_of_files_label(self.number_of_files)
            return
        elif validation == "Invalid":
            self.error_message("Invalid file", "All files must be XMLs")
            return
        else:
            self.frames[StartPage].change_number_of_files_label(self.number_of_files)

    def next(self):
        """
        checking the user input- if everything is ok moving to "run" function
         (not to second page- it is currently unused_
        """
        if not len(self.files):
            self.error_message("Invalid file", "No file Selected")
            return
        if self.output_entry.get() == "":
            self.error_message("Invalid entry", "Please enter output file name")
            return
        if self.error_rate_button.get() == "-1":
            self.error_message("Invalid choice", "Please choose error rate")
            return
        if self.running_options.get() == "-1":
            self.error_message("Invalid choice", "Please choose running mod")
            return
        self._update_file_names()

        if self.running_options.get() == "lysine" or self.running_options.get() == "default":
            #print("here")
            frame = SecondPage(self)
            self.frames[SecondPage] = frame
            self.frames[StartPage].grid_remove()    # remove so that tk will initialize the frame geometry
                                               # according to the second page
            frame.grid(row=0, column=0, sticky="nsew")
            self.show_frame(SecondPage)
        else:
            self.run()



    # def back_to_start_page(self):
    #     self.frames[SecondPage].grid_remove()   # remove so that tk will initialize the frame geometry
    #     self.frames[StartPage].grid()
    #     self.show_frame(StartPage)

    def _call_parser(self):
        """
        parser files one by one. add to the dict-list after parsing
        output name is with "_out" ending
        """
        for f, name in zip(self.files, self.file_names):
            # parser files one by one. add to the dict-list after parsing
            # output name is with "_out" ending
            #try:
                #print(self.swap_dict[f].get())
                swap = 0
                if f in self.swap_dict.keys() and self.swap_dict[f].get() == 1:
                    swap = 1
                self.dict_list.append(self.model.file_parse(f, str(f + '_out'), self.error_rate_button.get(),
                                                            self.running_options.get(), name, self.output_entry.get(), swap))
            #except:
                # it is kinda early stage to put a try-catch but i could not predict what will go wrong in the parser
                # and i didnt want it to have an interpreter error but a gui one
                # so i catch them all like pokemons
             #   self.error_message("Invalid file", "Cannot parse\ncould be wrong mode or an open xlsx in use")
              #  os._exit(1)

    def _merge_dicts(self, n):
        """
        n = number of files
        :return: dict of all parsed files combined
        """
        xlsx_outpsm(self.model.union_outPSm, self.output_entry.get(), self.files[0])
        merge_dict = {}
        protein_counter = dict()
        # print("hello")
        for i, d in zip(range(n), self.dict_list):
            for seq in d:
                if seq not in merge_dict:
                    merge_dict[seq] = United(seq, d[seq].prot, d[seq].counter, n, self.running_options.get(), d[seq].start,
                                             d[seq].end, d[seq].n_heavy, d[seq].n_light)
                    merge_dict[seq].update_in_file(i)
                    if self.running_options.get() == "default" or self.running_options.get() == "lysine":
                        merge_dict[seq].add_ratio(i, d[seq].ratio)
                        #added for heavy / light columns
                        merge_dict[seq].add_heavy1(i, d[seq].heavy)
                        merge_dict[seq].add_light1(i, d[seq].light)
                    elif self.running_options.get() == "label":
                        merge_dict[seq].add_all_label_mode(i, d[seq].counter, d[seq].peak_area,
                                                           d[seq].peak_intensity, d[seq].rt_seconds, d[seq].ions)

                else:
                    assert merge_dict[seq]
                    merge_dict[seq].update_in_file(i)
                    merge_dict[seq].add_sum_count(d[seq].counter)
                    merge_dict[seq].add_count_psm_heavy(d[seq].n_heavy)
                    merge_dict[seq].add_count_psm_light(d[seq].n_light)
                    if self.running_options.get() == "default" or self.running_options.get() == "lysine":
                        merge_dict[seq].add_ratio(i, d[seq].ratio)
                        #added for heavy / light columns
                        merge_dict[seq].add_heavy1(i, d[seq].heavy)
                        merge_dict[seq].add_light1(i, d[seq].light)

                    if self.running_options.get() == "label":
                        merge_dict[seq].add_all_label_mode(i, d[seq].counter, d[seq].peak_area,

                                                           d[seq].peak_intensity, d[seq].rt_seconds, d[seq].ions)
        for u in merge_dict.values():
            if u.protein in protein_counter.keys():
                temp = protein_counter[u.protein] + 1
                protein_counter[u.protein] = temp
            else:
                protein_counter[u.protein] = 1

        for u in merge_dict.values():
            if u.protein in protein_counter.keys():
                u.protein_count = protein_counter[u.protein]
            else:
                # shouldnt get here
                self.error_message("what?", "something went wrong with the united dict ")
                os._exit(1)

        unite_header = self.model.header_unite_create(n, self.running_options.get(), self.file_names)
        #print("bloooooooooooooooooooop")
        #print(protein_counter)
        if self.number_of_files > 6 :
            self.error_message("Notice", "more than 6 files, no venn will be produced\ncontinue...")
        try:
            self.model.xlsx_create(self.curr_dir +self.output_entry.get()+ "_united_file", merge_dict, unite_header,
                                    self.running_options.get())
            self.model.create_table_1(self.number_of_files)
        except:
            self.error_message("Invalid file", "Cannot parse\n an open xlsx in use")
            os._exit(1)



    def run(self):
        """
        TODO: this and all its functions should be in model. need to add "controller" to model..
         would be logically correct..

        call model.file_parser to parse each file in a loop
        check correctness
        call for merging
        :return:
        """

        self._call_parser()
        n = len(self.dict_list)
        assert (n == len(self.files))
        # print("all ok until united")
        # exit(0)
        if self.running_options.get() == "variable":
            try:
                self.model.create_table_2()
            except:
                self.error_message("Invalid file", "Cannot parse\n an open xlsx in use")
                os._exit(1)

        else:
            self._merge_dicts(n)

        self.error_message("Success", "Done!\nGoodbye and thanks for all the fish!")
        # did not find non-blocking join in python :( if i dont use os exit the other thread just keep running forever
        #os._exit(0)
        if platform.system() == 'Windows':
            subprocess.run(['explorer', os.path.realpath(self.curr_dir)])
        exit(0)

    def show_frame(self, curr_frame):
        frame = self.frames[curr_frame]
        frame.tkraise()

    def error_message(self, error_name, message):
        messagebox.showinfo(error_name, message)

    def main(self):
        self.mainloop()


class StartPage(tk.Frame):
    def __init__(self, controller: Controller):
        tk.Frame.__init__(self, controller.container)
        self.controller = controller
        self.change_label = self._design()  # number of files chosen

    def _design(self):
        """ function return label to adjust
        """
        request_file = tk.Label(self, text="Select all pep.xml files", font=MAIN_FONT, fg="LightBlue4")
        request_file.grid(column=0, row=0, padx=20, pady=10)
        button_browse = ttk.Button(self, text=" Browse ", command=self.controller.choose_file)
        button_browse.grid(column=0, row=1)
        file_ok = tk.Label(self, text="No files selected yet", font=("David", 10), fg="dim gray")
        file_ok.grid(column=0, row=2)
        request_output_name = tk.Label(self, text="Enter output file name", font=MAIN_FONT, fg="LightBlue4")
        request_output_name.grid(column=0, row=3, pady=5)
        self.controller.output_entry = tk.Entry(self)
        self.controller.output_entry.grid(column=0, row=4)
        request_error_rate = tk.Label(self, text="Select desired error rate", font=MAIN_FONT, fg="LightBlue4")
        request_error_rate.grid(column=0, row=5, pady=5)
        error_0 = tk.Radiobutton(self, text="0.000", variable=self.controller.error_rate_button, value="0.0000")
        error_001 = tk.Radiobutton(self, text="0.001", variable=self.controller.error_rate_button, value="0.0010")
        error_005 = tk.Radiobutton(self, text="0.005", variable=self.controller.error_rate_button, value="0.0050")
        error_01 = tk.Radiobutton(self, text="0.010", variable=self.controller.error_rate_button, value="0.0100")
        error_05 = tk.Radiobutton(self, text="0.050", variable=self.controller.error_rate_button, value="0.0500")
        error_0.grid(column=0, row=6)
        error_001.grid(column=0, row=7)
        error_005.grid(column=0, row=8)
        error_01.grid(column=0, row=9)
        error_05.grid(column=0, row=10)
        request_mod = tk.Label(self, text="Select running mode", font=MAIN_FONT, fg="LightBlue4")
        request_mod.grid(column=0, row=11, pady=5)
        default_mod = tk.Radiobutton(self, text="Default                    ",
                                     variable=self.controller.running_options, value="default")
        label_free_mod = tk.Radiobutton(self, text="Label free                 ",
                                        variable=self.controller.running_options,
                                        value="label")
        lysin_uniform_mod = tk.Radiobutton(self, text="K & uniform n-term", variable=self.controller.running_options,
                                           value="lysine")
        variable_mod = tk.Radiobutton(self, text="Variable                  ", variable=self.controller.running_options,
                                           value="variable")
        default_mod.grid(column=0, row=12)
        label_free_mod.grid(column=0, row=13)
        lysin_uniform_mod.grid(column=0, row=14)
        variable_mod.grid(column=0, row=15)

        #label_free = tk.Checkbutton(self, text="Label free mode", variable=self.controller.label_free,
                                #font=MAIN_FONT, fg="LightBlue4")
        #label_free.grid(column=0, row=10, pady=7)
        # TO DO!!!
        # i change it to "run" (used to be "next") button in the gui because im not using the second page
        # so it is actualy calling the "next" function and "next"  function call "run" function inside
        run_button = ttk.Button(self, text="Run", command=lambda: self.controller.next())
        run_button.grid(column=0, row=16, padx=20, pady=15)
        # lbl = ImageLabel(self)
        # lbl.grid(column=0)
        # lbl.load('phage.gif')
        return file_ok

    def browse(self):
        # Build a list of tuples for each file type the file dialog should display
        my_file_types = [('xml filles', '.xml'), ('all files', '.*')]
        files = askopenfilename(parent=self,
                               initialdir=os.getcwd(),
                               title="Please select a file:",
                               filetypes=my_file_types,
                                multiple=True)
        return list(files)

    def change_number_of_files_label(self, n):
        text = str(n) + " files have been selected"
        self.change_label = ttk.Label(self, text=text, font=("David", 10))
        self.change_label.grid(column=0, row=2)


class SecondPage(tk.Frame):
    def __init__(self, controller: Controller):
        tk.Frame.__init__(self, controller.container)
        self.controller = controller
        for item in controller.files:
            self.controller.swap_dict[item] = tk.IntVar()

        request_messege = tk.Label(self, text="Select  the \"swapped ratio\" files", font=MAIN_FONT,fg="LightBlue4")
        default_lable = tk.Label(self, text= "All unselected files get ratio = light/heavy", font=("David", 10), fg="LightBlue4")
        request_messege.grid(column=0, row=0, pady=5, padx=10, columnspan=2)
        default_lable.grid(column=0, row=1, columnspan=2)
        assert(controller.number_of_files == len(controller.files))
        for i in range(controller.number_of_files):
             check_button = tk.Checkbutton(self, text=controller.file_names[i],
                                           variable=self.controller.swap_dict[controller.files[i]],
                                           font=("Arial", 9))
             check_button.grid(column=0, row=i + 2, columnspan=2, sticky="W")

        curr_row = controller.number_of_files + 2
        # back_button = ttk.Button(self, text="Back", command=lambda: controller.back_to_start_page())
        # back_button.grid(row=curr_row, column=0)
        run_button = ttk.Button(self, text="Continue parsing",
                                 command=lambda: self._testing())
        run_button.grid(row=curr_row, column=1, padx=20, pady=20)

    def _testing(self):
        #print(self.controller.files)
        #for f in self.controller.swap_dict.values():
         #   print (f.get())
        self.controller.run()









if __name__ == '__main__':
    window = Controller()
    window.main()

