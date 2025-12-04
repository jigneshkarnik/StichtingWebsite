name: Create branch from labeled issue
on:
  issues:
    types: [labeled]
jobs:
  create-branch:
    if: github.event.label.name == 'in-progress' || github.event.label.name == 'start-work'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
    steps:
      - name: Create branch from main for issue
        uses: actions/github-script@v6
        with:
          script: |
            const issue = context.payload.issue;
            const owner = context.repo.owner;
            const repo = context.repo.repo;
            const octokit = github;
            const issueNumber = issue.number;
            // Build branch name: issue/<number>-short-title
            const rawTitle = issue.title.toLowerCase()
              .replace(/[^a-z0-9\s\-]/g, '')   // remove special chars
              .replace(/\s+/g, '-')            // spaces -> dashes
              .slice(0, 50);                   // limit length
            const branchName = `issue/${issueNumber}-${rawTitle}`;
            // Get SHA of main
            const mainRef = await octokit.rest.git.getRef({
              owner, repo, ref: 'heads/main'
            });
            const sha = mainRef.data.object.sha;
            // Create branch ref
            try {
              await octokit.rest.git.createRef({
                owner, repo, ref: `refs/heads/${branchName}`,
                sha
              });
              await octokit.rest.issues.createComment({
                owner, repo, issue_number: issueNumber,
                body: `Created branch \`${branchName}\` from \`main\`.`
              });
            } catch (err) {
              // If already exists, comment
              await octokit.rest.issues.createComment({
                owner, repo, issue_number: issueNumber,
                body: `Could not create branch \`${branchName}\`: ${err.message}`
              });
            }
