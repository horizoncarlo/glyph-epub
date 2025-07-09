const shell = require("terminal-kit").terminal;
const shellStringWidth = require("terminal-kit").stringWidth;
const EpubLib = require("epub");
const { convert } = require("html-to-text");

const book = new EpubLib("./books/The-White-Company_Conan-Doyle.epub");

const SHELL_HEIGHT_RESERVED = 2; // Number of lines reserved for UI elements, such as the top menu

const conversionOptions = {
  // preserveNewlines: true,
  // wordwrap: Math.floor(shell.width * 0.95),
  wordwrap: null,
};

const menuItems = [
  "File",
  "Edit",
  "View",
  "History",
  "Bookmarks",
  "Tools",
  "Help",
];

const menuOptions = {
  y: 1, // the menu will be on the top of the terminal
  // style: shell.inverse,
  style: shell.blue.bgRed,
  selectedStyle: shell.dim.blue.bgGreen,
  align: "center",
  fillIn: true,
};

let currentChapterIndex = null;
let fullChapter = null;
let currentPageText = null;
let currentLineIndex = null; // If a number we are paging within a chapter

shell.on("resize", (width, height) => {
  loadChapter();
});

let exitCount = 0;
shell.on("key", (name, matches, data) => {
  // shell("KEY PRESSED", name);

  switch (name) {
    case "PAGE_UP":
      if (currentLineIndex === null) {
        currentChapterIndex--;
      } else {
        currentLineIndex -= shell.height - SHELL_HEIGHT_RESERVED;

        if (currentLineIndex < 0) {
          currentLineIndex = null;
          currentChapterIndex--;
        }
      }
      loadChapter();
      break;
    case "PAGE_DOWN":
      if (currentLineIndex === null) {
        currentChapterIndex++;
      } else {
        currentLineIndex += shell.height - SHELL_HEIGHT_RESERVED;

        if (currentLineIndex > fullChapter?.length) {
          currentLineIndex = null;
          currentChapterIndex++;
        }
      }
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
    case "CTRL_C":
      shell.red("Exiting...");
      shell.processExit(0);
      break;
    default:
      exitCount = 0;
  }
});

function loadChapter() {
  const currentChapterId = getChapter()?.id;

  book.getChapter(currentChapterId, (err, html) => {
    const chapterText = convert(html, conversionOptions);
    fullChapter = shell.str(chapterText)?.split("\n") ?? [];

    // We need to page within our chapter
    if (fullChapter?.length > shell.height - SHELL_HEIGHT_RESERVED) {
      if (currentLineIndex === null) {
        currentLineIndex = 0;
      }

      currentPageText = fullChapter
        .slice(
          currentLineIndex,
          currentLineIndex + shell.height - SHELL_HEIGHT_RESERVED
        )
        .join("\n");
      // The entire chapter will fit in a single window
    } else {
      currentLineIndex = null;
      currentPageText = chapterText;
    }

    // shell.slowTyping(
    //   currentPageText,
    //   {
    //     style: shell.defaultColor,
    //     flashStyle: shell.brightWhite,
    //     // flashDelay: 1,
    //     // delay: 5,
    //   },
    //   function () {
    //     shell.processExit();
    //   }
    // );
    // });

    shell.clear();
    // shell.moveTo(1, 1).cyan(`${currentChapterId}\n\n`);

    shell.singleLineMenu(menuItems, menuOptions, (err, res) => {
      // console.log("MENU SELECTED callback", res);
    });

    shell.moveTo(1, 2).wrap(currentPageText);

    statusLine().magenta(
      "CURRENT PAGE TEXT lineCount=" +
        fullChapter?.length +
        ", HEIGHT=" +
        shell.height +
        " and calc=" +
        shellStringWidth(currentPageText),
      shellStringWidth(currentPageText) / shell.width
    );
  });

  //shell.spinner();
}

function getChapter() {
  return book?.flow?.[currentChapterIndex];
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
