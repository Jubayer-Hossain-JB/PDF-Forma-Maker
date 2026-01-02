from customtkinter import CTkButton, CTkFrame, CTkLabel, CTkImage, CTkCheckBox
from tkinter.messagebox import askokcancel
from PIL import Image
import tkinterdnd2
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter import Variable
from multiprocessing import Process, freeze_support
# import run
from os.path import splitext, dirname, join, basename
from os import mkdir

from PyPDF2 import PdfReader, PdfWriter, PageObject, Transformation
import math

class PdfStack():
    def init_step(self, input):
        self.reader = PdfReader(input)
        self.width = float(self.reader.pages[0].mediabox.width)
        self.height = float(self.reader.pages[0].mediabox.height)
        self.page_count = len(self.reader.pages)

        self.forma_page_width = 1656 #23*72        
        self.forma_page_height = 1296 #18*72

    
    def save_close(self, file_name, name):
        self.writer.add_metadata({
            '/Producer': 'PDF Writer',
            '/Title': "[Juri Book Binding]  of "+splitext(basename(file_name))[0],
            '/Author': 'Jubayer Hossain',
            '/Creator': 'JB Forma Maker'
        })
        saved_file = join(dirname(file_name), "[Juri Book Binding]  of "+splitext(basename(file_name))[0], name+".pdf")
        self.writer.write(saved_file)
        self.writer.close()
        
    def get_page(self, no):
        if no<self.page_count:
            return self.reader.pages[no]
        else:
            return PageObject().create_blank_page(width=self.width, height=self.height)
    def side_pages(self, job):
        new_pages = []
        
        for i in range(len(job)//2):   
            page_1 = job[i]
            page_2 = job[-i-1]
            if i%2 == 1:
                new_pages.append([page_2, page_1])
            else:
                new_pages.append([page_1, page_2])
                
        return new_pages
    
    def down_pages(self, job):
        new_pages = []
        for i in range(len(job)//2):
            page_1 = job[i]
            page_2 = job[-i-1]
            new_pages.append([page_2, page_1])
        return new_pages
        
    def layout4(self,input):
        self.init_step(input)
        valid_sheet = math.ceil(self.page_count/4)*4
        for i in range(valid_sheet//4):
            last_range = (i+1)*4
            if last_range>self.page_count:
                last = [PageObject.create_blank_page(width=self.width, height=self.height) for j in range(last_range-self.page_count)]
                for j in self.reader.pages[i*4:]: last.append(j)
                new_pages = self.side_pages(last)
            else: new_pages = self.side_pages(self.reader.pages[i*4:(i+1)*4]) 
            for p in new_pages:
                page = PageObject.create_blank_page(width=self.width*2, height=self.height)
                page.merge_page(p[0])
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(p[1])
                self.writer.add_page(p)  
        del new_pages
        del self.reader
        self.save_close(input)

    def layout8(self, input, Illustrator_editable):
        self.init_step(input)
        valid_sheet = math.ceil(self.page_count/8)*8
        count = 1
        try:
            mkdir(join(dirname(input), "[Juri Book Binding]  of "+splitext(basename(input))[0]))
        except: pass
        width_pad = (self.forma_page_height-self.width*2)/2
        height_pad = (self.forma_page_width-self.height*2)/2
        assert width_pad > 0
        assert height_pad > 0
        for i in range(valid_sheet//8):
            # last_range = (i+1)*8
            # if last_range>self.page_count:
            #     last = [PageObject.create_blank_page(width=self.width, height=self.height) for _ in range(last_range-self.page_count)]
            #     # for j in self.reader.pages[i*8:]: last.append(j)
            #     last = self.reader.pages[i*8:] + last
            #     new_pages = self.side_pages(last)
            # else:
            #     new_pages = self.side_pages(self.reader.pages[i*8:(i+1)*8])  
            # new_pages = self.down_pages(new_pages)
            new_pages = [[[4, 3], [0, 7]], [[2, 5], [6, 1]]] # 8 page formation of page ids
            for id,p in enumerate(new_pages):
                self.writer = PdfWriter()
                page = PageObject().create_blank_page(height=self.forma_page_width, width=self.forma_page_height) ## Potraite
                page.merge_page(self.get_page(p[0][0]+8*i)) 
                page.add_transformation(Transformation().translate(tx=self.width))               
                page.merge_page(self.get_page(p[0][1]+8*i))
                if Illustrator_editable: page.add_transformation(Transformation().translate(tx=-self.width,ty=self.height))
                else: page.add_transformation(Transformation().rotate(180).translate(tx=self.width, ty=self.height*2))
                page.merge_page(self.get_page(p[1][0]+8*i))
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(self.get_page(p[1][1]+8*i))
                page.add_transformation(Transformation().translate(tx=width_pad, ty=height_pad))
                self.writer.add_page(page)
                if id: self.save_close(input, f"[Forma {count}][Back]")
                else: self.save_close(input, f"[Forma {count}][Front]")
            count+=1
        del new_pages
        # del last_range
        del self.reader

    def layout16(self, input, Illustrator_editable):
        self.init_step(input)
        count = 1
        try:
            mkdir(join(dirname(input), "[Juri Book Binding]  of "+splitext(basename(input))[0]))
        except: pass
        width_pad = (self.forma_page_width-self.width*4)/2
        height_pad = (self.forma_page_height-self.height*2)/2
        if not (width_pad > 0):
            askokcancel(title = "Error", message="আপনার বইয়ের পৃষ্ঠার প্রস্থ কাঙ্খিত মাণের বেশি।\n দয়া করে তা ৫.৭৫ ইঞ্চির মধ্যে রাখুন।", icon="error")
            assert width_pad > 0

        if not (height_pad > 0):
            showerror(title = "Error", message="আপনার বইয়ের পৃষ্ঠার উচ্চতা কাঙ্খিত মাণের বেশি।\n দয়া করে তা ৯ ইঞ্চির মধ্যে রাখুন।", icon="error")
            assert height_pad > 0
        valid_sheet = math.ceil(self.page_count/16)*16
        # last_new_doc = []
        for i in range(valid_sheet//16):
            # last_range = (i+1)*16
            # if last_range>self.page_count:
            #     last = [PageObject.create_blank_page(width=self.width, height=self.height) for _ in range(last_range-self.page_count)]
            #     # for j in self.reader.pages[i*16:]: last.append(j)
            #     last = self.reader.pages[i*16:]+last
            #     new_pages = self.side_pages(last)

            # else:
            #     new_pages = self.side_pages(self.reader.pages[i*16:(i+1)*16])  

            # new_pages = self.down_pages(new_pages)
            # new_pages = self.side_pages(new_pages)
            new_pages = [[[[8, 7], [0, 15]], [[4, 11], [12, 3]]], [[[10, 5], [2, 13]], [[6, 9], [14, 1]]]] #16 page formation of page ids
            for id, p in enumerate(new_pages):
                self.writer = PdfWriter()
                page = PageObject().create_blank_page(width=self.forma_page_width, height=self.forma_page_height)
                page.merge_page(self.get_page(p[1][0][0]+16*i)) # +16*i converting to real page ids from range 16
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(self.get_page(p[1][0][1]+16*i))
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(self.get_page(p[0][0][0]+16*i))
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(self.get_page(p[0][0][1]+16*i))
                if Illustrator_editable: page.add_transformation(Transformation().translate(tx=(-3)*self.width,ty=self.height))
                else: page.add_transformation(Transformation().rotate(180).translate(tx=self.width, ty=self.height*2))
                page.merge_page(self.get_page(p[0][1][0]+16*i))
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(self.get_page(p[0][1][1]+16*i))
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(self.get_page(p[1][1][0]+16*i))
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(self.get_page(p[1][1][1]+16*i))
                page.add_transformation(Transformation().translate(tx=width_pad, ty=height_pad))
                self.writer.add_page(page)
                if id: self.save_close(input, f"[Forma {count}][Back]")
                else: self.save_close(input, f"[Forma {count}][Front]")
            count+=1
        del new_pages
        # del last_range
        # del last_new_doc
        del self.reader


working_dir = dirname(__file__)
class Gui(tkinterdnd2.Tk):
    def __init__(self,*kwargs):
        super().__init__(*kwargs)

        self.iconbitmap(join(working_dir,'icon.ico'))
        self.geometry("500x500+500+120")
        self.resizable(False, False)
        self.title("Easy Forma Maker")
        self.gif_frames = []
        self.done_frames = []

        self.idx = 0
        self.layout_mode = 8
        self.file_path = ""

        label = CTkLabel(self,text="Make Booklet From PDF", font=("Roboto-Regular", 30))
        label.pack(pady=20)
        self.bind('<ButtonPress-1>', self.start)
        self.bind('<B1-Motion>', self.move)
        
        body_frame = CTkFrame(self, fg_color="#444444", corner_radius=15)
        body_frame.place(rely=0.15,relx=0.5,relwidth=.98, relheight=0.9, anchor='n')

        layouts = CTkFrame(body_frame,fg_color='transparent')
        layouts.pack(pady="8")

        # self.booklet4 = CTkButton(layouts, text="4", font=("Roboto-Regular", 60),height=150, width=150, command= lambda: self.change_mode(4))
        self.booklet8 = CTkButton(layouts,  text="8", font=("Roboto-Regular", 60),height=150, width=150, fg_color="#363636",  border_width=3,command= lambda: self.change_mode(8))
        self.booklet16 = CTkButton(layouts,  text="16", font=("Roboto-Regular", 60),height=150, width=150, command= lambda: self.change_mode(16))
        # self.booklet4.pack(padx=9,anchor='n',side='left')
        self.booklet8.pack(padx=8,anchor='n',side='left')
        self.booklet16.pack(padx=8,anchor='n',side='left')
        self.checkbox = Variable(self)
        CTkCheckBox(body_frame,checkbox_width=20, checkbox_height=20,font=("Roboto-Regular", 16),text="Illustrator Editable",variable= self.checkbox).pack()
            
        self.img = CTkImage(Image.open(join(working_dir,'resource/upload-icon.png')),size=(80,80))
        self.run = CTkImage(Image.open(join(working_dir, 'resource/run.png')), size=(80,80))
        self.upload = CTkButton(body_frame, text="Upload PDF",font=("Roboto-Regular", 20), corner_radius=25, height=100, image=self.img, fg_color="#222222", hover_color="#303030", command=self.filedi)
        self.upload.pack(fill='x',padx=9, expand=True,)

        self.cancel_but = CTkButton(self.upload, text="Cancel", width=28, height=28, fg_color="#a40000", hover_color= "#670000", command=self.cancel)

        self.upload.drop_target_register(tkinterdnd2.DND_FILES)
        self.upload.dnd_bind('<<Drop>>', self.drop)
        self.load_frames()
    
    def start(self,e):
        self.x,self.y= e.x,e.y
    def move(self,e):
        self.geometry("+%d+%d"%(e.x-self.x+self.winfo_x(),e.y-self.y+self.winfo_y()))
        
    def drop(self, e):
        f_name= e.data[1:-1].split("} {")[0]
        if splitext(f_name)[1]==".pdf":
            self.file_path = f_name
            self.start_but()

    def filedi(self):
        f_name = askopenfilename(filetypes=[("Only PDF Files", "*.pdf")],)
        if f_name:
            self.file_path = f_name
            self.start_but()
        
    def change_mode(self, e):
        # self.booklet4.configure(fg_color="#3B8ED0",border_width=0)
        self.booklet8.configure(fg_color="#3B8ED0",border_width=0)
        self.booklet16.configure(fg_color="#3B8ED0",border_width=0)
        if e == 4: 
            self.booklet4.configure(fg_color="#363636",border_width=3)
            self.layout_mode = 4
        elif e == 8: 
            self.booklet8.configure(fg_color="#363636",border_width=3)
            self.layout_mode = 8
        elif e == 16: 
            self.booklet16.configure(fg_color="#363636",border_width=3)
            self.layout_mode = 16

    def start_but(self):
        self.upload.configure(text ="Start", image=self.run, command=lambda: self.run_proccess(self.file_path))
        self.cancel_but.grid(row=2, column=4, sticky='w', padx=20)
    def cancel(self):
        self.cancel_but.grid_forget()
        self.upload.configure(image=self.img, text="Upload PDF", command=self.filedi)

    def run_proccess(self, input):
        self.cancel_but.grid_forget()
        self.output = join(dirname(input), "ready_layout "+basename(input))
        self.upload.drop_target_unregister()
        self.upload.configure(state="disabled")
        if self.layout_mode==4: func = engine.layout4
        elif self.layout_mode == 8:func = engine.layout8
        else: func = engine.layout16
        self.t = Process(target=func, args=(input,self.checkbox.get()))
        self.t.start()
        self.animate_proc()
    def load_frames(self):
        for i in range(1,37):
            self.gif_frames.append(Image.open(join(working_dir,f"resource/frames/animation ({i}).png")))
        for i in range(1,29):
            self.done_frames.append(Image.open(join(working_dir,f"resource/done_frames/frame ({i}).png")))
    def animate_proc(self):
        self.upload.configure(image=CTkImage(self.gif_frames[self.idx], size=(80,80)), text="Processing...")
        self.idx +=1
        if self.idx > 35: self.idx = 0
        if self.t.is_alive():self.after(84, self.animate_proc)
        else:
            self.idx=0
            self.done()
    def done(self):
        self.upload.configure(image=CTkImage(self.done_frames[self.idx], size=(80,80)), text="Done")
        self.idx +=1
        if self.idx < 28:
            self.after(80, self.done)
        else:
            # popen(self.output)
            self.upload.configure(image=self.img,state="normal", text="Upload PDF", command=self.filedi)
            self.upload.drop_target_register(tkinterdnd2.DND_FILES)

if __name__ == "__main__":
    freeze_support()
    engine = PdfStack()
    root = Gui()
    root.mainloop()

