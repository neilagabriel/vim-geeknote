# vim-geeknote

[Geeknote](http://www.geeknote.me) Plugin for Vim. Under active development.

## Supported Features

- Open notebook and note listing in a vertical split navigation pane.
- Open notes for reading by selecting them in the navigation pane.
- Notebook creation
- Editing note content.

## Dependencies

- Vim 7.4.364 or newer (issues observed with earlier versions)

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

## Acknowledgments

- [Geeknote](http://www.geeknote.me)
- [The Nerd Tree](https://github.com/scrooloose/nerdtree)
- [Vim Plugin Starter Kit](https://github.com/JarrodCTaylor/vim-plugin-starter-kit)

## Todo

- Note creation
- Note title modification
- Note movement (notebook to notebook)
- Tag support
- Toggle close
- Temp-file cleanup
- Evernote (re)sync
- Prettier navigation window
- Improved notebook creation process
- Vim help
