# Git quick-help for CSIRO datacube training environment

  - [Introduction](#introduction)
  - [Help for any git command](#help-for-any-git-command)
  - [Global configuration options](#global-configuration-options)
  - [General workflow for a shared github or bitbucket repository](#general-workflow-for-a-shared-github-or-bitbucket-repository)
  - [General workflow for your own repository](#general-workflow-for-your-own-repository)
  - [Trouble-shooting](#trouble-shooting)
  - [More about branches](#more-about-branches)
  - [More about submodules](#more-about-submodules)
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

## Create a branch

## Git add and commit

## Push your branch to the remote repository

## Create a pull request

## Initialise an existing code directory

## Add or edit the location of the remote repository
The remote repository is where you will ```pull``` from and ```push``` to. It is commonly referred to by the alias "origin".
```
# If required, add a definition for "origin"
git remote add origin [remote-url]

# Change the url of the remote repository
git remote set-url origin [new-url]
```

stackoverflow
- [git-remote-add-origin-vs-remote-set-url-origin](https://stackoverflow.com/a/47194962)

## Check the status of your local repository

## Stash any changes you may have made

## Revert any files you may changed

## Trouble-shooting

Git is quite good at providing information about why it can not perform an operation. However, it can be daunting running a command when you're not sure what it may do. If in doubt, we recommend ask the internet or phone a friend. Stackoverflow is an excellent resource for understanding what a command will do and which commands to use in sequence. 

## More about branches

Branches are a powerful and necessary feature of git for collaborative teams but can be daunting to new users. At its simplest, you can create your own branch - locally - make changes locally. At any time you can commit your branch to the remote repository, and when your changes are ready you can submit your branch as a pull request to the 'main' branch. The 'main' branch may commonly be 'master' or 'develop'.

Branching works within git by tracking individual commits, and by managing any file-level conflicts during a merge between branches. If there are conflicts git will ask to you resolve them; git will merge automatically only when there are no file-level conflicts - this is the common case when you know your changes wont affect other parts of the code. The pull request and review procedure allows one of your collaborators to assess your changes for any implications in the rest of the code.

We encourage you to read more about branching:
- [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model)

## More about submodules

The CSIRO EASI Training repository contains the datacube-core repository as a tagged submodule from https://github.com/opendatacube. The datacube-core submodule is regularly tested and updated (re-tagged), which helps manage any changes that may be required in the CSIRO EASI Training repository.

Sometimes you will need to re-syncronise your local copy of the datacube-core submodule against the updated (re-tagged) version in the CSIRO EASI Training repository.
```
To do: How best to manage any local changes you may have made to datacube-core

git submodule update --init --recursive
git pull origin master
```

stackoverflow
- [git-submodules-and-rebase](https://stackoverflow.com/a/16700914)


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
