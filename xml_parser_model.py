
import re
from utils.parserPep import ParserPep, Variable
import xlsxwriter
from venn import venn
import os
from matplotlib import pyplot as plt
from collections import Counter

class Model:

    def __init__(self):
        self.reader = None
        self.dict_table_1 = {}  # key = file short name, values (list) = psm. pep, stripped
        self.dict_table_2 = {}  # key = file short name, values(list) = n_all, n_heavy, k_all, k_heavy
        self.union_modification_set = set()#union of all "ParserPep.pep_modification_set" from all files
        self.union_stripped_pep = set() # union of all peptides seq in all dictionary.
        self.union_outPSm = list()
        # should be the same as numbers of lines in united file, but i was stupid then so this is easier
        self.peptide_sets_dict = dict()     # for table 1 venn diagrams
        self.stripped_sets_dict = dict()    # for table 1 venn diagrams
        self.output_file_name = ""  # the name of the united file insert by user. update in file_parse func
        self.psm_list_dict = dict()         # for table 1 venn diagrams
        self.proteins_sets_dict = dict()    # for table 1 venn diagram
        self.file_names_by_order = list()
        self.curr_dir = ""


    def validation(self, files, n):
        # n= number of files
        if n == 0:
            # user did not choose files
            return "Exit"
        for i in range(n):
            if not re.search(r"\.xml$", files[i]):
                # if not all files are XML files
                return "Invalid"
        else:
            return "Valid"

    def xlsx_create(self, output_file_name, dict_peptides, header, mode):
        """"
        export the data to excel sheet
        """
        workbook = xlsxwriter.Workbook(output_file_name + '.xlsx')
        sheet = workbook.add_worksheet()
        headers = header
        headers_len = len(headers)
        for x in range(headers_len):
            sheet.write(0, x, headers[x])
        # col and raw are just for the for iterations below
        row = 1
        for pep in dict_peptides:
            if mode == -1:
                ll = [pep] + dict_peptides[pep]
            else:
                ll = dict_peptides[pep].class_to_list(mode)
            if headers_len == 17:
                print("headers len is " + str(headers_len))
                print("ll len is " + str(len(ll)))
                print(headers)
            #print((headers_len))
            #print(len(ll))
            assert (headers_len == len(ll))
            for x in range(headers_len):

                sheet.write(row, x, ll[x])
            row += 1
        workbook.close()  # creating the output.xlsx

    def header_unite_create(self, num_of_files, mode, file_names):
        headers = ["seq", "protein", "counter all", "before", "after"]
        assert (num_of_files == len(file_names))
        if mode == "default" or mode == "lysine":
            #assert (mode == 0)
            for f in file_names:
                headers.append("ratio " + str(f))
                headers.append("logRatio " + str(f))
                headers.append("heavy_area " + str(f))
                headers.append("light_area " +str(f))
            headers.append("mean")
            headers.append("median")
            headers.append("st dev")
        elif mode == "label":
            #assert (mode == 1)
            for f in file_names:
                headers.append("count in file " + str(f))
            for f in file_names:
                headers.append("peak area " + str(f))
            for f in file_names:
                headers.append("peak intensity " + str(f))
            for f in file_names:
                headers.append("rt seconds " + str(f))
            for f in file_names:
                headers.append("matched ions " + str(f))

        headers.append("count")
        headers.append("protein count")
        headers.append("count psm heavy")
        headers.append("count psm light")

        return headers

    def file_parse(self, file_name, output_name, error_rate, mode, short_name,output_name_united, swap):
        print("start " + str(short_name) + ", swap = " + str(swap))
        self.output_file_name = output_name_united
        #print(self.output_file_name)
        if mode == "variable":
            f = Variable(file_name, mode, output_name_united)
        else:
            f = ParserPep(file_name, mode, output_name_united)
        f.parse_dict(error_rate, swap)
        self.union_outPSm = self.union_outPSm + f.list_outPSM
        dict_f = f.dict_peptides
        if mode == "variable":
            values = f.var_modifications
            self.dict_table_2[short_name] = values
            return dict_f  #empty dict in this case
        f.update_psm_pep_and_stripped()
        values = [f.psm, f.peptide_modification_counter, f.stripped_pep, len(f.protein_set)]
        self.dict_table_1[short_name] = values
        self.peptide_sets_dict[short_name] = f.pep_modification_set
        self.stripped_sets_dict[short_name] = set(f.dict_peptides.keys())
        self.proteins_sets_dict[short_name] = f.protein_set
        #print(len(f.protein_set))
        #print(self.dict_table_1)
        self.union_modification_set = self.union_modification_set.union(f.pep_modification_set)
        self.union_stripped_pep = self.union_stripped_pep.union(f.dict_peptides.keys())
        self.psm_list_dict[short_name] = f.psm_list
        if mode == "lysine":
            headers = ["seq", "type(semi/full)", "protein", "alternative protein", "probability", "start", "end", "counter",
                       "k mod heavy", "k mod light", "no k", "sum heavy", "sum light", "ratio", "min_expect"]
            self.xlsx_create(output_name, dict_f, headers, mode)
        if mode == "default":
            headers = ["seq", "type(semi/full)", "protein", "alternative protein", "probability", "start", "end", "counter",
                       "n mod heavy", "n mod light", "sum heavy", "sum light", "ratio", "min_expect"]
            self.xlsx_create(output_name, dict_f, headers, mode)
        elif mode == "label":
            headers = ["seq", "type(semi/full)", "protein", "alternative protein", "probability", "start", "end",
                       "counter", "sum peak area", "sum peak intensity", "avg rt seconds", "matched ions", "min_expect"]
            self.xlsx_create(output_name, dict_f, headers, mode)

        return dict_f

    def _union_prots_set(self, set_):
        for s in self.proteins_sets_dict.values():
            set_ = set_.union(s)

        return set_

    def create_table_1(self, number_of_files):
        print("start table 1")
        total_psm = 0
        for v in self.dict_table_1.values():
            total_psm += v[0]
        union_prots = self._union_prots_set(set())
        #union_peptides = union_peptides.union(self.proteins_sets_dict.values())

        #print(len(union_prots))
        self.dict_table_1["total"] = [total_psm, len(self.union_modification_set), len(self.union_stripped_pep),
                                      len(union_prots)]
        headers_table_1 = ["", "PSM", "Peptides", "Stripped peptides", "proteins"]
        self.xlsx_create(self.curr_dir +"psm_peptides_stripped_prots_table_"+self.output_file_name, self.dict_table_1, headers_table_1, -1)
        if len(self.stripped_sets_dict) == 1:
            return
        if number_of_files > 6:
            return
        venn(self.peptide_sets_dict)
        plt.title("peptides intersections")
        plt.savefig(self.curr_dir +"venn_peptides_" + self.output_file_name +".png")
        venn(self.stripped_sets_dict)
        plt.title("stripped intersections")
        plt.savefig(self.curr_dir+"venn_stripped_" + self.output_file_name + ".png")
        venn(self.proteins_sets_dict)
        plt.title("proteins intersections")
        plt.savefig(self.curr_dir +"venn_proteins_" + self.output_file_name + ".png")
        self.updated_lists_for_venn()




    def update_file_names(self):
        for key in self.psm_list_dict.keys():
            self.file_names_by_order.append(key)

    def list_to_wise_set(self, list):
        dicti_dict = dict()
        for n in range(len(list)):
            if list[n] in dicti_dict.keys():
                dicti_dict[list[n]] = dicti_dict[list[n]] + 1
                list[n] = list[n] + str(dicti_dict[list[n]])

            else:
                dicti_dict[list[n]] = 0
        return list

    def updated_lists_for_venn(self):
        for key in self.psm_list_dict.keys():
            self.psm_list_dict[key] = set(self.list_to_wise_set(self.psm_list_dict[key]))
        #self.lil_test()
        venn(self.psm_list_dict)
        plt.title("PSM intersections")
        plt.savefig(self.curr_dir +"venn_PSM_" + self.output_file_name + ".png")


    def lil_test(self):
        self.update_file_names()
        a = self.psm_list_dict[self.file_names_by_order[0]]
        b = self.psm_list_dict[self.file_names_by_order[1]]
        c = self.psm_list_dict[self.file_names_by_order[2]]
        ab = len(list((Counter(a) & Counter(b)).elements()))
        ac = len(list((Counter(a) & Counter(c)).elements()))
        cb = len(list((Counter(c) & Counter(b)).elements()))
        print(ab)
        print(ac)
        print(cb)


    def create_table_2(self):
        print("start table 2")
        set_header = set()
        new_dict = dict()
        for d in self.dict_table_2.values():
            for v in d.keys():
                set_header.add(v)
                temp = str(v)[0] +" all"
                set_header.add(temp)
        set_header =list(set_header)
        set_header.sort()
        set_header.insert(0, "")
        #print(set_header)

        for name, values in zip(self.dict_table_2.keys(), self.dict_table_2.values()):
            final_list = list()
            flag = 0
            for mod in set_header:
                if "all" in str(mod):
                    #print(mod)
                    #print(str(mod[0]))
                    for k in values.keys():
                        if str(k).startswith(str(mod[0])):  # if it is the right "all"
                            flag = 1
                            temp = values[k]
                            #print(temp)
                            final_list.append(temp[1])    # append the "count all in file"
                            #print(final_list)
                            break
                elif mod in values.keys():
                    flag = 1
                    temp = values[mod]
                    final_list.append(temp[2])
                if flag == 0:
                    final_list.append(" ")

                flag = 0
            #print(final_list)
            del final_list[0]
            new_dict[name] = final_list

        if "n all" in set_header:
            set_header[set_header.index("n all")] = "n all (PSM)"
            #print(set_header)
            #print(new_dict)
            #os._exit(8)

        self.xlsx_create(self.curr_dir +"variable_table_" + self.output_file_name,new_dict,
                         set_header, -1)














