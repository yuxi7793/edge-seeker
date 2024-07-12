# README #

Welcome to the UChicago Project Lab Community Repo where you will be able to share in a truly open source manner all the brilliant ideas and fails that you come up with. 

Here are some tips that if you learn to follow religiously you will begin a love affair with GIT that will last a lifetime and if you will ignore at your own risk and be a glutton for merge punishment.

One of the reasons we are teaching you this is so that you can leverage this super power when you graduate and are in the real world.

### Procedures for commiting code

* You are not permitted to push code to the "main" banch; to edit code you must create a branch first.  

git clone <repo url>  

### create a branch on the webpage to develop your code changes in
* git fetch
* git checkout <branch>
* git add <files>
* git commit -a -m "commit message"
* git push
* create pull request on the webpage to merge using "rebase and fast forward"

### If you have a branch, and someone else has merge their branch to main resulting in your branch being outdated, you can rebase your branch on main this way:
* git checkout main
* git pull --rebase
* git checkout my-branch
* git rebase main
* git push -f origin my-branch

### How do I tell if my branch is out of date?
Go to the branches page on the bitbucket website
Select all branches
Hover over the modal for your branch and it will say how many commits ahead and behind you are.  You must be 0 behind main before you can push 
