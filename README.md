# vim-geeknote

[Geeknote](http://www.geeknote.me) Plugin for Vim. Under active development.

## Supported Features

- Notebook and note viewing, renaming, and creation.
- Editing note content.

## Screenshots

![img](https://github.com/neilagabriel/vim-geeknote/blob/master/img/explorer.png)

## Dependencies

- Vim 7.4.364 or newer (issues observed with earlier versions)

## Known Issues

- Depending on formatting, note content is sometimes lost when saving notes. The data may be retrieved by reading the temp file that was created for the note (most often under /temp). This is actually an issue with Geeknote itself. See [Geeknote#223](https://github.com/VitaliyRodnenko/geeknote/issues/223).

- Infrequently, errors are encountered while connecting with the Evernote server to download the user data. See [Geeknote#224](https://github.com/VitaliyRodnenko/geeknote/issues/224). To know if you're hitting this issue, exit vim and run geeknote standalone and see if it is able to list your notes (i.e. `geeknote list`).
  
## Installation

1. If you have not done so already, install [Geeknote](http://www.geeknote.me)
   and login to make sure it is functional. You must login before attempting to
   use the plugin.

2. Use your plugin manager of choice to install plugin.

- [Vundle](https://github.com/gmarik/vundle)
  - Add `Bundle 'https://github.com/neilagabriel/vim-geeknote'` to .vimrc
  - Run `:BundleInstall`
- [Pathogen](https://github.com/tpope/vim-pathogen)
  - `git clone https://github.com/neilagabriel/vim-geeknote ~/.vim/bundle/vim-geeknote`

3. Optional mappings:

    noremap <F8> :Geeknote<cr>

## Usage

Use `:Geeknote` to open/toggle the geeknote navigation window. If the
navigation window is not visible, this command will split the current window
vertically and display the navigation window on the left-side. If visible, the
navigation window will be hidden. Notebooks can be expanded to show the notes
they contain.  To expand a notebook, simply navigate to the name of the
notebook and hit `<Enter>`. Hit `<Enter>` again to close the notebook. To
open/view a note navigate to the note and hit `<Enter>`. The note will be
displayed in the previous window if it is possible to do so or in a new
vertical split. To save changes to the note, simply save the buffer (e.g.
`:w`).

Use `:GeeknoteCreateNotebook <name>` to create a new notebook.

Use `:GeeknoteCreateNote <name>` to create a new note. The note will be created
in the notebook currently selected in the navigation window. If a notebook is
not selected, the note will be created in the default notebook. A new buffer
for the note will be displayed in the previous window if it is possible to do
so or in a new vertical split. The note will not be created until the buffer is
saved (e.g. `:w`). Once saved, the note will be created and the navigation
window will update.

Use `:GeeknoteSync` to update the navigation with the latest data on the
Evernote server. Warning, any notes that are opened when this command is issued
will not be updated. Support for this will be added in future releases.

To rename notebooks or notes, simply modify the the name of the notebook/note
in the navigation window and save the bugger (e.g. `:w`). Any number of changes
can be made before saving, but be sure not to modify an item's GUID.

To move a note into a different notebook, simply move the note's text (includes
title and GUID) under the desired notebook in the navigation window and save
the buffer. Similar to renaming, any number notes can be moved before saving
the buffer.

## Acknowledgments

- [Geeknote](http://www.geeknote.me)
- [The Nerd Tree](https://github.com/scrooloose/nerdtree)
- [Vim Plugin Starter Kit](https://github.com/JarrodCTaylor/vim-plugin-starter-kit)

## Todo

- Refresh open notes upon `:GeeknoteSync`
- Tag support
- Prettier navigation window
- Improved notebook creation process
- Vim help
