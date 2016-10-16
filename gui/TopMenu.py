# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import Tkinter as tk
import json
import copy

import logging
logger = logging.getLogger('mars_logging')

class TopMenu(tk.Menu):
    '''
    This class loads in a json file from "config_file"
    and dynamically generates functions based off of the commands
    specified within. Additionally you may define custom commands
    in the top menu in the init_ui method

    Note: Our current json file is operations.json defined locally to
        this file
    '''
    def __init__(self, parent, config_file, queue, name):
        tk.Menu.__init__(self, parent)
        self.client_queue_in = queue
        self.name = name

        self.command_menu = tk.Menu(self, tearoff = 0)
        self.client_menu = tk.Menu(self, tearoff = 0)
        self.init_ui(config_file, name)
        self.existing_roots = {'Mars Commands': { 'parent': None, 'menu': self.command_menu }}

    def init_ui(self, config_file, name):
        '''
        Pulls in all commands from operations.json
        '''
        commands_config = self.load_commands(config_file)

        for key, val in commands_config.iteritems():
            copyval = '%s' % val['command']
            if val['options'] is None:
                self.command_menu.add_command(label=key, command=self.commandFunc(copyval))
            else:
                options = tk.Menu(self, tearoff=0)
                
                for opt in val['options']:
                    options.add_command(label=opt, command=self.commandFunc(copyval, opt))
                self.command_menu.add_cascade(label=key, menu=options)

    def get_parent_tree(self, i, roots):
        delim = '/'
        arr = roots[0:(i + 1)]
        return delim.join(arr)

    def add_menu_item(self, commandName, function, menuRoot = None):
        '''
        Adds a new menu item to the TopMenu. 
        name: Displayed name of the command
        function: callback function assigned when button is clicked
        root: MenuItem to append the new operation under
            None: Root level
            Else: For example: View/blah will make a menu item "View" and append "blah" underneath with the given function.
        '''
        if menuRoot is not None:
            roots = menuRoot.split('/')
            #establish root exists
            if roots[0] not in self.existing_roots:
                print 'adding', roots[0]
                menu = tk.Menu(self, tearoff = 0)
                self.existing_roots[roots[0]] = {'parent': None, 'menu' : menu}
            
            #make all menus up to given function
            for i in range(1, len(roots)):
                root = roots[i]
                root_parent = self.get_parent_tree(i, roots)
                if root_parent not in self.existing_roots:
                    print 'adding', root_parent
                    menu = tk.Menu(self, tearoff = 0)
                    self.existing_roots[root_parent] = {'parent': self.get_parent_tree(i - 1, roots), 'menu' : menu}
            
            #append our function to the last root
            self.existing_roots[menuRoot]['menu'].add_command(label = commandName, command = function)
        else:
            self.add_command(label=commandName, command = function)

    def get_highest_delim(self):
        maxSize = 0
        keys = []
        for key in self.existing_roots:
            rootSize = len(key.split('/'))
            if rootSize > maxSize:
                keys = [key]
                maxSize = rootSize
            elif rootSize == maxSize:
                keys.append(key)
        return (maxSize, keys)

    def get_parent_menu_tuple(self, key):
        return self.existing_roots[key]['parent'], self.existing_roots[key]['menu']

    def finalize_menu_items(self):  
        '''
        Adds all existing_roots and submenus to root
        We do this after all add_menu_items are called
        because if we do it on add, then the first add
        is the final add, so we need versatility
        '''
        #updates topmenu with given command_menu
        size, keys = self.get_highest_delim()
        print size, keys
        while size > 1:
            #go through each non-root menu and adds them to their parent
            for key in keys:
                parent, key_menu = self.get_parent_menu_tuple(key)
                print 'adding', key, 'to', parent
                self.existing_roots[parent]['menu'].add_cascade(label = key.replace(parent + '/', ''), menu = key_menu)
                self.existing_roots.pop(key, None)
            size, keys = self.get_highest_delim()

        # we now only have roots, add them all to self
        for key in self.existing_roots:
            self.add_cascade(label = key, menu = self.existing_roots[key]['menu'])
    
    def commandFunc(self, cmd, option=False):
        '''
        Because of memory referencing in python, we use a functional technique
        to avoid referencing the same variable the whole time.
        '''
        if option == False:
            command = cmd
        else:
            command = cmd + ' ' + option
        
        def topMenuFunctionReference():
            logger.debug('Piping "' + command + '" to the client')
            self.client_queue_in.put(command)
        
        return topMenuFunctionReference

    def load_commands(self, config_file):
        '''
        Loads in local Command json file
        '''
        with open(config_file) as f:
            configuration = \
                json.load(f)
        return configuration

if __name__=='__main__':
    from Queue import Queue
    root = tk.Tk()
    q = Queue()
    t = TopMenu(root, '../gui/operations.json', q)
    root.config(menu=t)
    #t.grid()
    root.update()
    print t.winfo_height(), t.winfo_width()
    root.mainloop()

