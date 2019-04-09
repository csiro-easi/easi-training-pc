# Git quick-help for CSIRO datacube training environment

  - [Introduction](#introduction)
  - [Help for any git command](#help-for-any-git-command)
  - [Global configuration options](#global-configuration-options)
  - [Unstaged changes](#unstaged-changes)
  - [Revert changes to a file](#revert-changes-to-a-file)
  - [Undo Add](#undo-add)
  - [Move changes in current branch to a new branch](#move-changes-in-current-branch-to-a-new-branch)
  - [Create a Pull request](#create-a-pull-request)
  - [Merge a branch locally](#merge-a-branch-locally)
  - [Make changes to a file after its been "add"ed (but not commited)](#make-changes-to-a-file-after-its-been-added-but-not-commited)

*Note: This document is a work in progress*

## Introduction
Git is a document version control system. It retains a full history of changes to all files (including deleted ones) by tracking incremental changes and recording a history timeline of changes. Changes you make append to the history timeline.

Git allows you to copy ("clone") a repository, make changes to files, and "commit" and "push" these changes back to the source repository. Git does not specifically require nor define a master or parent repository but in practice its useful to agree on a central repository that combines the work of all contributers. GitHub (www.github.com) and BitBucket (e.g., www.bitbucket.csiro.au) are examples of central repositories.
* Github is open to all. Its very good for open-source collaboration and sharing between organisations and individuals. The free teir makes all repositories publicly available. Private repositories are only available in one of the paid tiers. Most users use the free teir of GitHub.
* Bitbucket is part of the Atlassian suite (Confluence, Jira, etc) and is usually available within an organisation only. By defalt all repositories are private to the organisation. Selected repositories can be made public.

## Help for any git command
```git [cmd] --help```

Search [StackOverflow](www.stackoverflow.com) (no need to Login or Sign up).

## Global configuration options
Global configuration file applies across all your working directories. A local configuration file has the same format and keys but applies only to the working directory it is in.

In your home directory or project driectory create a ```.gitignore``` file. Recommended contents:
```
git config --global user.name "[your name]"  # Necessary for commits
git config --global user.email "[your email]"  # Necessary for commits
git config --global color.ui auto
git config --global core.excludesfile [path to excludes file]  # See below
git config --global core.editor vim  # Your favourite editor
git config --global merge.tool vimdiff  # Your favourite diff tool, if applicable
git config --global core.sharedRepository group  # Sets group sharing option for cloned repositories on shared systems
```

A Git 'excludes' file tells Git to ignore given files and paths when comparing your local directory contents with the Git history timeline.

In your home directory or project driectory create a ```.gitignore``` file. Suggested contents include:
```
*.pyc
Thumbs.db
.DS_Store
.ipynb_checkpoints
```

## Unstaged changes
You attempt to update you working directory with a ```git pull``` however you have changes in your working directory and git cannot complete the update.
```git stash```
Save the current state of your working directory, and allow you to return to a 'clean' working directory.

## Revert changes to a file
You have made some changes to a file but you don't wish to keep them
```git checkout -- [filename]```
You can use ```git checkout [filename]``` but in this case the checkout command is also used for changing to a different branch, so if your filename happens to be the same name as a branch, you will get the branch instead.

## Undo Add
You have done ```git add [file]``` and wish to revert this. You have not done ```git commit``` yet.
```git reset [file]```
Reset will remove it from the "about to be committed" list.

## Move changes in current branch to a new branch
You have made changes in the current branch (e.g,. master) but now wish to move these changes to a new branch to separate your development.
```
git checkout -b [new branch]  # create a new branch; your changes remain
git add [files]  # as usual
git commit -m [message]  # as usual
# create a Pull request or Merge the branch
```

## Create a Pull request

## Merge a branch locally
```
git checkout [target branch]  
git merge [source branch]
```

## Make changes to a file after its been "add"ed (but not commited)
Git manages changes to files, not the files themselves. Redo ```git add [files]```.