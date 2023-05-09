% -------------------------------------------------------------------
%  @LaTeX-class-file{
%     filename        = "CSDEXEThesis.cls",
%     codetable       = "ISO/ASCII",
%     keywords        = "LaTeX, University of Exeter, Thesis, CSD",
%     docstring       = "Class for a CSD thesis."
%	author	="Dr. Riccardo Di Clemente under CC0 Licence"
% --------------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{CSDEXEThesis}[CSDEXE Thesis Class]



% -- GENERAL SETUP --

% type
\LoadClass[11pt, a4paper]{report}

% page geometry
\RequirePackage[
  headheight=2cm,
  top=3cm,
  bottom=3cm,
  footskip=1.5cm,
  footnotesep=1cm,
  left=2.5cm,
  right=2.5cm,
  a4paper
]{geometry}

% export in PDF/X, PDF/A, etc...
\RequirePackage{etoolbox}
\RequirePackage{colorprofiles}
\RequirePackage[a-2b,mathxmp]{pdfx}[\today]

% language, font and encodings
\RequirePackage{newpxtext,newpxmath}
\RequirePackage[T1]{fontenc}
\RequirePackage[english]{babel}



% -- USEFUL PACKAGES --

% spacings (\onehalfsize, \doublesize)
\RequirePackage{setspace}

% indent first line of paragraph
\RequirePackage{indentfirst}

% captions
\RequirePackage{caption}
\RequirePackage{subcaption}

% footnotes
\RequirePackage{footnote}
\RequirePackage[bottom]{footmisc}

% mathematics
\RequirePackage{amsmath}
\RequirePackage{comment}

% links
\RequirePackage{hyperref}
\RequirePackage{url}

% colors
\RequirePackage{color}

% graphics
\RequirePackage{graphicx}

% algoritms
\RequirePackage{algorithm}
\RequirePackage{algorithmic}

% code snippets
\RequirePackage{listings}

% plots, drawings etc...
\RequirePackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta}

% references
\RequirePackage[autostyle]{csquotes}
\RequirePackage[backend=biber]{biblatex}
\addbibresource{references.bib}



% -- DEFINITIONS --

% university
\def\university#1{\gdef\@university{#1}}

% master name
\def\mastername#1{\gdef\@mastername{#1}}

% academic Year
\def\academicYear#1{\gdef\@academicYear{#1}}

% student ID
\def\studentId#1{\gdef\@studentId{#1}}

% advisor
\def\advisor#1{\gdef\@advisor{#1}}

% co-advisor (if one)
\def\coadvisor#1{\gdef\@coadvisor{#1}}
\def\coadvisorsUniversity#1{\gdef\@coadvisorsUniversity{#1}}

% university of Exter color
\definecolor{UniExeterColor}{RGB}{7, 66, 151}
 
% degree type
\def\degree#1{\gdef\@degree{#1}}


% -- LINKS SETUP --

% set all links to black color
\hypersetup{
  colorlinks,
  citecolor=black,
  filecolor=black,
  linkcolor=black,
  urlcolor=black
}



% -- ITEMS AND ENUMARATIONS --

% reduce spacing for items and enumerations
\let\saveditemize=\itemize
\let\savedenditemize=\enditemize
\renewenvironment{itemize}
  {\begin{spacing}{0.5}\saveditemize}
  {\savedenditemize\end{spacing}}

\let\savedenumerate=\enumerate
\let\savedendenumerate=\endenumerate
\renewenvironment{enumerate}
  {\begin{spacing}{0.5}\savedenumerate}
  {\savedendenumerate\end{spacing}}

% italic for quotes
\let\savedquote\quote
\let\endsavedquote\endquote
\renewenvironment{quote}
    {\itshape\savedquote}
    {\endsavedquote}



%-------------------- Certification to storage -----------
\newif\ifcertify
\certifytrue

\newcommand{\certifysi}{%
	\ifcertify
		\makebox[0pt][l]{\raisebox{0.15ex}{\hspace{0.1em}$\checkmark$}}%
	\fi
	$\square$%
}
\newcommand{\certifyno}{%
	\ifcertify\else
		\makebox[0pt][l]{\raisebox{0.15ex}{\hspace{0.1em}$\checkmark$}}%
	\fi
	$\square$%
}	


%-------------------- Permison to storage -----------
\newif\ifshare
\sharetrue

\newcommand{\sharesi}{%
	\ifshare
		\makebox[0pt][l]{\raisebox{0.15ex}{\hspace{0.1em}$\checkmark$}}%
	\fi
	$\square$%
}
\newcommand{\shareno}{%
	\ifshare\else
		\makebox[0pt][l]{\raisebox{0.15ex}{\hspace{0.1em}$\checkmark$}}%
	\fi
	$\square$%
}







% -- HEADERS AND FOOTERS --

% custom headers and footers
\RequirePackage{fancyhdr}

% custom title style
\RequirePackage{titlesec}

% remove headers and footers in blank pages
\RequirePackage{scrextend}

% box for titles
\RequirePackage{adjustbox}

% style for chapters
\titleformat{\chapter}[display]
{\Huge\filleft}
{
  \minsizebox{!}{70pt}{\colorbox{UniExeterColor}{\color{white} \thechapter}}
}
{1.2ex}
{}

% style for sections
\titleformat{\section}[hang]
{\Large}
{
  \colorbox{UniExeterColor}{\color{white} \thesection}
}
{1ex}
{\scshape}

% style for subsections
\titleformat{\subsection}[hang]
{\large}
{
  \colorbox{UniExeterColor}{\color{white} \thesubsection}
}
{1ex}
{\scshape}

% style for subsubsections
\titleformat{\subsubsection}[hang]
{\normalsize}
{}
{0ex}
{\bfseries\scshape}

% remove line headers
\renewcommand{\headrulewidth}{0ex}

% style for headers and footers
\newcommand{\setfancyhf} {
  \fancyhf{}
  \fancyhead[RO]{{\footnotesize\leftmark}}
  \fancyhead[LE]{{\footnotesize\rightmark}}
  \fancyfoot[RE, LO]{}
  \fancyfoot[C]{\thepage}
}



% -- FRONTMATTER --

\newcommand{\frontmatter} {
    
  % set roman page numbering
  \pagenumbering{roman}

  % set page style
  \pagestyle{fancy}

  % create cover
  \maketitle

  % reset fancy headers
  \setfancyhf

  % set head witdth
  \setlength{\headwidth}{\textwidth}

  % custom titles
  \renewcommand{\listfigurename}{List of Figures}
  \renewcommand{\listtablename}{List of Tables}
  \renewcommand{\listalgorithmname}{List of Algorithms}
  \renewcommand{\lstlistingname}{Code} % Caption name of code snippets
  \renewcommand{\lstlistlistingname}{List of Code Snippets}
  \def\listacronymname{List of Acronyms}

  \def\abstractname{Abstract}
 

  \renewcommand{\bibname}{References}

  \def\acknowledgmentsname{Acknowledgments}

  % insert abstract
  \abstractpage

  % insert table of contents
  \tableofcontents
%  \cleardoublepage

  % insert list of figures
  %\phantomsection
  \addcontentsline{toc}{chapter}{\listfigurename}
  \listoffigures
 % \cleardoublepage

  % insert list of tables
  %\phantomsection
  \addcontentsline{toc}{chapter}{\listtablename}
  \listoftables
 % \cleardoublepage

  % insert list of algorithms
  %\phantomsection
  \addcontentsline{toc}{chapter}{\listalgorithmname}
  \listofalgorithms

  % insert list of code snippets
  %\phantomsection
  \addcontentsline{toc}{chapter}{\lstlistlistingname}
  \lstlistoflistings
 % \cleardoublepage

  % insert list of abbreviations/acronyms
  \acronyms
}



% -- TITLE/COVER --

% insert watermark
\RequirePackage{watermark}

\renewcommand{\maketitle} {
  %set custom geometry
  \newgeometry{
    top=1.5cm,
    bottom=2cm,
    inner=2cm,
    outer=2cm,
    headheight=3.5cm,
    includehead,
    includefoot,
  }

  % set head witdth
  \setlength{\headwidth}{\textwidth}

  % set watermark
  \thiswatermark{
    \centering
    \put(-380,-700) {
      \includegraphics[width=1.2\linewidth]{res/arms_exeter_logo_bg}
    }
  }

  % set academic year in footer
  \cfoot{
  %\put(-330,0){\includegraphics[width=1.3\linewidth]{res/bottom}}
  \normalsize\textsc{Academic Year \\ \@academicYear}
  }

  % set brands in header
  \lhead{
    \includegraphics[height=3cm]{res/exeter_logo}
  }
  \rhead{
    \includegraphics[height=3cm]{res/CSD}
  }

  % content
  \begin{center}

    % master name
    \null \vspace{\stretch{2}}
    \normalsize\textsc{
      \@degree\\ 
       \@mastername
    } \\

    % title
    \vspace{3ex}
    \LARGE\textbf{\@title} \\
    \vspace{\stretch{3}}

    % authors, advisors etc...
    \doublespacing

    \begin{flushleft}
      \small
      \textsc{Candidate} \hfill \textsc{Supervisor} \\
      \large{\textbf{\@author}} \hfill \large{\textbf{\@advisor}} \\
      \small
      \textbf{Student ID \@studentId} \hfill \textbf{\@university} \\
      % insert co-advisor if not empty
      \ifx\@coadvisor\empty \else
        \hfill \\
        \hfill \textsc{Co-supervisor} \\
        \hfill \large{\textbf{\@coadvisor}} \\
        \small
        \hfill \textbf{\@coadvisorsUniversity} \\
      \fi
    \end{flushleft}

    \vspace{\stretch{1}} \null
  \end{center}

  % restore defaults
  \cleardoublepage
  \restoregeometry
  \onehalfspacing
}


% -- ACRONYMS/ABBREVIATIONS --

\RequirePackage{acronym}

% custom style for acronyms
\newcommand{\acronyms}{
  \phantomsection
  \addcontentsline{toc}{chapter}{\listacronymname}
  \chapter*{\listacronymname}
  \input{frontmatter/glossary}
 % \cleardoublepage
}



% -- ABSTRACT --

\renewenvironment{abstract}[1][en] {
  \null \vfill
  \begin{center}
    \bfseries
     {\large \abstractname}
  \end{center}
} {
  \vfill   	
  \noindent  \begin{tabular}{lcc}
  & Yes & No\\
		{\begin{minipage}{12cm} \footnotesize  I certify that all material in this dissertation which is not my own work has been identified.\end{minipage}} & 
 \certifysi &  \certifyno \\[20pt]%	
 				{\begin{minipage}{12cm} \footnotesize I give the permission to the Department of Computer Science of the University of Exeter to include this manuscript in the institutional repository,  exclusively for academic purposes.\end{minipage}} & 	
							  \sharesi &  \shareno \\
									 	
				\end{tabular}
  
}

\newcommand{\abstractpage} {
  % set empty style for this page (no headers and footers)
  \thispagestyle{empty}

  % english version
  \input{frontmatter/abstract}
  

}



% -- MAIN MATTER --

\newcommand{\mainmatter} {
  \cleardoublepage

  % reset page counter
  \setcounter{page}{1}

  % set arabic page numbering
  \pagenumbering{arabic}

  % reset chapter counter
  \setcounter{chapter}{0}
}



% -- BACKMATTER --

\newcommand{\backmatter}{
  %\cleardoublepage
  \phantomsection

  % add references
  \addcontentsline{toc}{chapter}{\bibname}
  \printbibliography
  
  %\cleardoublepage
  \phantomsection

  % add acknowledgments
  \addcontentsline{toc}{chapter}{\acknowledgmentsname}
  \acknowledgments
}



% -- ACKNOWLEDGMENTS --
\newcommand{\acknowledgments} {
  \phantomsection
  \chapter*{\acknowledgmentsname}
  \input{frontmatter/thanks}
}


% -- CODE SNIPPETS --

% Colors for code snippets highlights
\definecolor{commentsColor}{RGB}{36, 161, 156}
\definecolor{numColor}{RGB}{71, 96, 114}
\definecolor{stringColor}{RGB}{205, 63, 62}
\definecolor{kwColor}{RGB}{248, 6, 204}
\definecolor{bgCodeColor}{RGB}{255, 249, 249}

% Style of code snippets
\lstdefinestyle{codeSnippet} {
  backgroundcolor=\color{bgCodeColor},
  commentstyle=\color{commentsColor},
  keywordstyle=\color{kwColor},
  numberstyle=\tiny\color{numColor},
  stringstyle=\color{stringColor},
  basicstyle=\ttfamily\footnotesize,
  breakatwhitespace=false,         
  breaklines=true,                 
  captionpos=b,                    
  keepspaces=true,                 
  numbers=left,                    
  numbersep=5pt,                  
  showspaces=false,                
  showstringspaces=false,
  showtabs=false,                  
  tabsize=2
}

\lstset{style=codeSnippet}