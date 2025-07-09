const shell = require("terminal-kit").terminal;
const shellStringWidth = require("terminal-kit").stringWidth;
const EpubLib = require("epub");
const { convert } = require("html-to-text");

const fs = require('fs');
const path = require('path');
const logPath = path.join(__dirname, 'debug.log');
function log(message) {
  const timestamp = new Date().toISOString();
  const line = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(logPath, line);
}
log("START NEW INSTANCE");

const book = new EpubLib("./books/The-White-Company_Conan-Doyle.epub");

const SHELL_HEIGHT_RESERVED = 1; // Number of lines reserved for UI elements, such as the bottom status line

const conversionOptions = {
  // preserveNewlines: true,
  // wordwrap: Math.floor(shell.width * 0.95),
  wordwrap: null,
};

let fullChapter = null;
let currentChapterIndex = null;
let currentPageText = null;
let currentLineIndex = null; // If a number we are paging within a chapter

shell.on("resize", (width, height) => {
  loadChapter();
});

let exitCount = 0;
shell.on("key", (name, matches, data) => {
  /* TODO Ideas
   Help - replace content with hotkeys
   Table of Contents - also maybe jump?
   Better status line at the bottom
   Custom line wrap, toggle on then input field of number which replaces screen.width wrap
     Do shell.wrapColumn({ width: 30 }); once outside of loadChapter. width = null resets to terminal width
   slowTyping is a cool function, not sure we have a use
   Basic search/find with match highlighting in current page (only?)
   Loading from command line arg and from in the app (using .fileInput?)
   */
  switch (name) {
    case "HOME":
      currentLineIndex = null;
      loadChapter();
      break;
    case "END":
      currentLineIndex = fullChapter?.length - shell.height;
      loadChapter();
      break;
    case "CTRL_HOME":
      currentLineIndex = null;
      currentChapterIndex = 0;
      loadChapter();
      break;
    case "CTRL_END":
      currentLineIndex = null;
      currentChapterIndex = book.flow?.length;
      loadChapter();
      break;
    case "PAGE_UP":
    case "LEFT":
      // TODO Bit janky going from say chapter 2 to chapter 1, as it jumps to ch1 but line 0 instead of line end-of-ch1 minus shell height
      if (currentLineIndex === null) {
        currentChapterIndex--;
      } else {
        currentLineIndex -= shell.height - SHELL_HEIGHT_RESERVED;
      }
      loadChapter();
      break;
    case "PAGE_DOWN":
    case "RIGHT":
      if (currentLineIndex === null) {
        currentChapterIndex++;
      } else {
        currentLineIndex += shell.height - SHELL_HEIGHT_RESERVED;
      }
      loadChapter();
      break;
    case "UP":
      currentLineIndex--;
      loadChapter();
      break;
    case "DOWN":
      currentLineIndex++;
      loadChapter();
      break;
    case "ESCAPE":
    case "q":
    case "Q":
      exitCount++;
      if (exitCount === 1) {
        statusLine()
          .yellow("Press ")
          .bold(name.toLowerCase())
          .yellow(" again to exit...");
      } else if (exitCount > 1) {
        shell.processExit(0);
      }
      break;
    // TODO Open file...nice in theory to use the built in, but it's a bit janky, and it'd be fun instead to make our own
    // case "SHIFT_F1":
    //   shell.clear();
    //   shell(`Open a file from ${os.homedir()}`);
    //   shell.fileInput(
    //     { baseDir: os.homedir() } ,
    //     function( error , input ) {
    //       if ( error )
    //       {
    //         shell.red.bold("\nAn error occurs: " + error + "\n");
    //       }
    //       else
    //       {
    //         shell.green("\nYour file is '%s'\n" , input);
    //       }
    //     }
    //   );
    //   break;
    case "CTRL_C":
      shell.red("Exiting...");
      shell.processExit(0);
      break;
    default:
      exitCount = 0;
  }
});

function loadChapter() {
  if (currentLineIndex < 0) {
    currentLineIndex = null;
    currentChapterIndex--;
  }
  if (currentLineIndex >= fullChapter?.length) {
    currentLineIndex = null;
    currentChapterIndex++;
  }
  
  if (currentChapterIndex < 0) {
    log("Cannot page back further, reached zero end of chapter index=" + currentChapterIndex);
    currentChapterIndex = 0;
  }
  else if (currentChapterIndex > book.flow?.length) {
    log("Ran out of chapters to move to with index=" + currentChapterIndex + " vs " + book.flow.length);
    currentChapterIndex = book.flow.length;
  }
  
  shell.hideCursor();
  
  const currentChapterId = getChapterObj()?.id;
  book.getChapter(currentChapterId, (err, html) => {
    const chapterText = convert(html, conversionOptions);
    // TTODO Splits properly BUT doesn't account for wrapping, so we'll often get a double line jump when using arrow up/down
    // fullChapter = shell.str(chapterText)?.split("\n") ?? [];
    fullChapter = wrapTextToTerminalLines(chapterText);
    
    log("Current line index is " + currentLineIndex + " vs count " + fullChapter?.length);

    // We need to page within our chapter
    if (fullChapter?.length > shell.height - SHELL_HEIGHT_RESERVED) {
      if (currentLineIndex === null) {
        currentLineIndex = 0;
      }

      log(`From line index=${currentLineIndex} and to=${currentLineIndex + shell.height - SHELL_HEIGHT_RESERVED} in chapter index=${currentChapterIndex} (${currentChapterId})`);
      log("First line is: " + fullChapter[0]);
      currentPageText = fullChapter
        .slice(
          currentLineIndex,
          currentLineIndex + shell.height - SHELL_HEIGHT_RESERVED
        )
        .join("\n");
      log("Now converting to text the first line is: " + currentPageText.substring(0, 100));
    }
    // The entire chapter will fit in a single window
    else {
      log("Entire chapter (" + currentChapterIndex + ") fits on one page");
      currentLineIndex = null;
      currentPageText = chapterText;
    }

    shell.clear();
    shell.wrap(currentPageText);
    
    statusLine().magenta(
      `Status: w${shell.width}/h${shell.height}, line=${currentLineIndex} of ${fullChapter?.length} in chapter=${currentChapterIndex} (${currentChapterId})`
    );
    
    shell.hideCursor();
  });

  //shell.spinner();
}

function wrapTextToTerminalLines(text) {
  const spaceWidth = 1;
  const resultLines = [];
  const paragraphs = text.split('\n');
  
  for (const paragraph of paragraphs) {
    // Handle cases where an original line was empty or contained only whitespace
    if (paragraph.trim().length === 0) {
      resultLines.push('');
      continue;
    }
    
    // Split the paragraph into words. Using /\s+/ handles multiple spaces and tabs.
    // Filter out any empty strings that might result from multiple spaces.
    const words = paragraph.split(/\s+/).filter(word => word.length > 0);
    
    // If a paragraph had no actual words (e.g., just spaces), push an empty line.
    if (words.length === 0) {
        resultLines.push('');
        continue;
    }
    
    let currentLine = '';
    let currentLineWidth = 0;
    
    for (const word of words) {
      const wordWidth = shellStringWidth(word);
      
      // Case 1: The current line is empty (first word on a new line)
      if (currentLine.length === 0) {
        currentLine = word;
        currentLineWidth = wordWidth;
      }
      // Case 2: Adding the word (with a leading space) fits on the current line
      else if (currentLineWidth + spaceWidth + wordWidth <= shell.width) {
        currentLine += ' ' + word;
        currentLineWidth += spaceWidth + wordWidth;
      }
      // Case 3: Adding the word (with a leading space) does NOT fit but the word itself fits on a new line
      else if (wordWidth <= shell.width) {
        resultLines.push(currentLine);
        currentLine = word;
        currentLineWidth = wordWidth;
      }
      // Case 4: The word itself is longer than the terminal width, so it must be broken
      else {
        if (currentLine.length > 0) {
          resultLines.push(currentLine);
        }
        
        currentLine = '';
        currentLineWidth = 0;

        for (const char of word) {
          const charWidth = shellStringWidth(char);
          if (currentLineWidth + charWidth <= shell.width) {
            currentLine += char;
            currentLineWidth += charWidth;
          } else {
            resultLines.push(currentLine);
            currentLine = char;
            currentLineWidth = charWidth;
          }
        }
      }
    }
    
    if (currentLine.length > 0) {
      resultLines.push(currentLine);
    }
  }

  return resultLines;
}

// TTODO Works well but isn't performant due to looping character by character
// function wrapTextToTerminalLines(text) {
//   const lines = [];
//   const lineArray = text.split('\n');

//   for (const currentLine of lineArray) {
//     let line = '';
//     for (const currentWord of currentLine) {
//       const lineWidth = shellStringWidth(line);
//       const charWidth = shellStringWidth(currentWord);

//       if (lineWidth + charWidth > shell.width) {
//         lines.push(line);
//         line = currentWord;
//       } else {
//         line += currentWord;
//       }
//     }
//     lines.push(line);
//   }

//   return lines;
// }

function getChapterObj() {
  return book.flow?.[currentChapterIndex];
}

function statusLine(msg) {
  const toReturn = shell.moveTo(1, shell.height).eraseLine();
  if (msg) {
    return toReturn.wrap(msg);
  }
  return toReturn;
}

book.on("end", function () {
  shell.windowTitle(book.metadata.title);

  if (!book.flow?.length) {
    shell.red("No chapters found in book");
    shell.processExit(-1);
    return;
  }

  if (currentChapterIndex === null) {
    currentChapterIndex = 0;
  }

  loadChapter();
});

// shell.fullscreen();
// shell.grabInput({ mouse: "button" });
shell.grabInput();
book.parse();
