My [talon](https://talonvoice.com) config

# Overview

## Basic alphabet

`air bat cap drum each fine gust harp sit jury crunch look made near odd pit quench red sun trap urge vest whale plex yank zip`

I prefer these over the default letters:

* `door/dip` - d
* `far` - f
* `hope` - h
* `ice` - i
* `king` - k
* `oy/oil` - o
* `tea` - t
* `box` - x

## Key overrides

* enter - use / apply
* escape - scape
* backspace - junk
* shift - sky / ship
* command - kemmed
* home - pop
* end - push
* undo - ups

## Skipping, selecting, deleting whole words

### \<num> before / \<num> after

Jumps over \<num> words to the left or right (cursor can be in the middle of the word before jumping)

### \<num> befores / \<num> afters

Selects \<num> words to the left or to the right

### delete \<num> befores / delete \<num> afters

Deletes \<num> words to the left or to the right

### correct

Selects last insertion

## Repetition

### \<any command> \<num> ok

`go down 5 ok?` - I love saying that with an implied question mark

### wink [num]

repeats the last command \[num] or 1 times

### again \[num] / back \[num]

Special commands that hook up to other commands as forward/backward actions or as "extend action". The direct repeaters like `wink` are great, but you lose them every time you say any command other than the one you want to repeat.

Again/back are attached to commands that are commonly repeated, for example, search forward (`cmd-g`) after search (`cmd-f`).

The inspiration for this feature came from [anonfunc/talon-user](https://github.com/anonfunc/talon-user/blob/master/apps/editor.py#L180) extension logic.

**Examples of how again/back works**

* after search (`cmd-f`) the again/back commands are `cmd-g` and `cmd-shift-g` (search forwards or backwards)
* after `2 befores` (having 2 words selected), `again 2` results in 4 words selected, `back` results in 1 words selected
* after `next tab` command, the again is `ctrl-tab` and back is `ctrl-shift-tab`

<img width="406" alt="image" src="https://user-images.githubusercontent.com/1171003/66724002-3a185180-edd5-11e9-9866-01839299f4ae.png">

The last repeatable command is shown in the bottom of the phrase history along with the shortcuts that will be performed for again/back.

### Picking a previous command
If you're lazy like me, you don't want to say long commands over and over, all latest repeatable commands are stored and can be re-sent by saying `re-run` and picking the right command from the picker that pops up.


## Named clipboard

`copy <word>` - copies selection indexed by \<word>
 
 `(free | paste) <word>` - paste clipping stored under \<word>
  
 `show clips` - show what's saved in the named clipboard
 
 <img width="406" alt="image" src="https://user-images.githubusercontent.com/1171003/67542290-0543ae80-f6a1-11e9-9e26-7f50c5cfc7e9.png">


## Smart parameterized macro

`macro start` - to start recording a new macro sequence. The macro sequence will be shown as it is recorded. It will keep showing in the phrase history as long as you're using it.

`macro stop` - to stop recording

<img width="406" alt="image" src="https://user-images.githubusercontent.com/1171003/68077581-7828e580-fd83-11e9-8b6b-b4137290ad18.gif">

The script in [`macro.py`](./macro.py) now supports a number argument.
You can record a macro with a number in it, like a complex vim command - ```ys1aw]``` (surround around 1 word\[s] with square brackets)

`macro play` / `replay` - will play the macro as recorded  

`replay 5` -  will play the key sequence with 5 instead of 1 - ```ys5aw]```  

`replay 1 1` -  will play the key sequence with 11 instead of 1 - ```ys11aw]```

---

## Inspiration

Most of the code in this repo was scavenged from or inspired by other members of the talon community:

[anonfunc/talon-user](https://github.com/anonfunc/talon-user)

[2shea/talon_configs](https://github.com/2shea/talon_configs)

[seananderson/talon-config](https://github.com/seananderson/talon-config)

[dwiel/talon_community](https://github.com/dwiel/talon_community)
