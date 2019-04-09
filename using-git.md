# Git quick-help for CSIRO datacube training environment

  - [Introduction](#introduction)
  - [Help for any git command](#help-for-any-git-command)
  - [Global configuration options](#global-configuration-options)
  - [General workflow for a shared github or bitbucket repository](#general-workflow-for-a-shared-github-or-bitbucket-repository)
  - [General workflow for your own repository](#general-workflow-for-your-own-repository)
  - [Additional topics](#additional-topics)

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

In your home directory or project driectory create a ```.gitconfig``` file. Recommended contents:
```
git config --global user.name "[your name]"      # Necessary for commits
git config --global user.email "[your email]"    # Necessary for commits
git config --global color.ui auto
git config --global core.excludesfile [path to excludes file]  # See below
git config --global core.editor vim              # Your favourite editor
git config --global merge.tool vimdiff           # Your favourite diff tool, if applicable
git config --global core.sharedRepository group  # Sets group sharing option for repositories on shared systems
```

A Git 'excludes' file tells Git to ignore given files and paths when comparing your local repository contents with the Git history timeline.

In your home directory or project driectory create a ```.gitignore``` file. Suggested contents include:
```
*.pyc
Thumbs.db
.DS_Store
.ipynb_checkpoints
```

## General workflow for a shared github or bitbucket repository
The effective way to work with a shared repository is to use a branch for your edits.

First time only
1. [Clone to a local repository](#clone-to-a-local-repository)

General workflow
1. [Check which branch you are in](#check-which-branch-you-are-in)
2. [Pull any remote changes](#pull-any-remote-changes)
3. [Create a branch](#create-a-branch)
4. Make your changes
5. [Git add and commit](#git-add-and-commit)
6. [Push your branch to the remote repository](#push-your-branch-to-the-remote-repository)
7. [Create a pull request](#create-a-pull-request)

## General workflow for your own repository
The primary difference is that you tend to make and commit your changes directly in the master branch.

First time only
1. Create an empty repository on github or bitbucket
2. Either
    - [Clone to a local repository](#clone-to-a-local-repository)
    - Copy your existing files into the local repository
3. Or
    - [Initialise an existing code directory](#initialise-an-existing-code-directory)
    - [Add or edit the location of the remote repository](#add-or-edit-the-location-of-the-remote-repository)
4. [Git add and commit](#git-add-and-commit)
5. [Push your branch to the remote repository](#push-your-branch-to-the-remote-repository)

General workflow
1. [Check the status of your local repository](#check-the-status-of-your-local-repository)
2. Either
    - [Stash any changes you may have made](#stash-any-changes-you-may-have-made) (save changes for later)
    - Or
    - [Revert any files you may changed](#revert-any-files-you-may-changed) (delete changes)
3. [Pull any remote changes](#pull-any-remote-changes)
4. Make your changes
5. [Git add and commit](#git-add-and-commit)
6. [Push your branch to the remote repository](#push-your-branch-to-the-remote-repository)

## Additional topics
*Add useful topics as required*

<hr>

## Clone to a local repository
The full URL of a repository is often available as copy/paste from the host. HTTPS and SSH protocols will work equally as well. Clone will create a local repository in a directory named ```repository name```. 
```
$ git clone [URL of remote repository/repository name]

# Clone will set the remote repository location and 'origin' alias
$ cd [repository name]
$ git remote -v
```

## Check which branch you are in
List the local and available remote branches. The curent local branch has an asterix next to it.
```
$ git branch -a
```

## Pull any remote changes
Pull is a combination of ```fetch``` and ```merge```. Pull will attempt to apply remote updates directly into the current branch; it should fail with a useful message if there are local changes, in which case some combination of ```stash```, ```rebase``` or ```reset``` should help. If the current branch is tracking the remote branch then branch name is not required.
```
$ git pull origin [branch]
```

- [What is the difference between 'git pull' and 'git fetch'?](https://stackoverflow.com/q/292357)
- https://blog.mikepearce.net/2010/05/18/the-difference-between-git-pull-git-fetch-and-git-clone-and-git-rebase/

## Create a branch

## Git add and commit

## Push your branch to the remote repository

## Create a pull request

## Initialise an existing code directory

## Add or edit the location of the remote repository

## Check the status of your local repository

## Stash any changes you may have made

## Revert any files you may changed


<hr>

*Clean-up these topics and move any useful ones to [Additional topics](#additional-topics)*

## Unstaged changes
You attempt to update you working directory with a ```git pull``` however you have changes in your working directory and git cannot complete the update.

Save the current state of your working directory, and allow you to return to a 'clean' working directory.
```
git stash
git pull origin master
git stash pop
```

stackoverflow
- [git-pull-keeps-telling-me-to-stash-local-changes-before-pulling](https://stackoverflow.com/a/20569627)
- [git-stash-and-git-pull](https://stackoverflow.com/a/12476984)

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

## Merge a branch locally
```
git checkout [target branch]  
git merge [source branch]
```

## Make changes to a file after its been "add"ed (but not commited)
Git manages changes to files, not the files themselves. Redo ```git add [files]```.