# vim-geeknote

[Geeknote](http://www.geeknote.me) Plugin for Vim. Under active development.

## Supported Features

- Notebook and note viewing and creation.
- Editing note content.

## Dependencies

- Vim 7.4.364 or newer (issues observed with earlier versions)

## Known Issues

- Depending on formatting, note content is sometimes lost when saving notes. The data may be retrieved by reading the temp file that was created for the note (most often under /temp). This is actually an issue with Geeknote itself. Investigating.
  
## Installation

1. Clone and install geeknote from my personal geeknote fork ([neilagabriel/geeknote](https://github.com/neilagabriel/geeknote)). See [Geeknote](http://www.geeknote.me) webpage for installation
   instructions. This is a temporary install step that will become unnecessary when my changes are merged into the mainline geeknote repository.

2. Login with geeknote ('geeknote login') and verify it is functional.

3. Use your plugin manager of choice to install plugin.

- [Vundle](https://github.com/gmarik/vundle)
  - Add `Bundle 'https://github.com/neilagabriel/vim-geeknote'` to .vimrc
  - Run `:BundleInstall`
- [Pathogen](https://github.com/tpope/vim-pathogen)
  - `git clone https://github.com/neilagabriel/vim-geeknote ~/.vim/bundle/vim-geeknote`

## Usage

Use `:Geeknote` to open the geeknote navigation window. This command will split
the current window vertically and display the navigation window on the
left-side. Notebooks can be expanded to show the notes they contain.  To expand
a notebook, simply navigate to the name of the notebook and hit `<Enter>`. Hit
`<Enter>` again to close the notebook. To open/view a note navigate to the note
and hit `<Enter>`. The note will be displayed in the previous window if it is
possible to do so or in a new vertical split. To save changes to the note,
simply save the buffer (e.g. `:w`).

Use `:GeeknoteCreateNotebook <name>` to create a new notebook.

Use `:GeeknoteCreateNote <name>` to create a new note. The note will be created
in the notebook currently selected in the navigation window. If a notebook is
not selected, an error is displayed. A new buffer for the note will be
displayed in the previous window if it is possible to do so or in a new
vertical split. The note will not be created until the buffer is saved (e.g.
`:w`). Once saved, the note will be created and the navigation window will
update.

## Acknowledgments

- [Geeknote](http://www.geeknote.me)
- [The Nerd Tree](https://github.com/scrooloose/nerdtree)
- [Vim Plugin Starter Kit](https://github.com/JarrodCTaylor/vim-plugin-starter-kit)

## Todo

- Note title modification
- Note movement (notebook to notebook)
- Tag support
- Toggle close
- Temp-file cleanup
- Evernote (re)sync
- Prettier navigation window
- Improved notebook creation process
- Vim help
