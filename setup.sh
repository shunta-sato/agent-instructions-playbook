#!/bin/sh

set -eu

usage() {
    cat <<'EOF'
Usage: ./setup.sh [WORKDIR]

Expose this repository's skills to Codex, GitHub Copilot, and Claude Code in
WORKDIR. WORKDIR defaults to the current directory and must be a Git worktree
root.
EOF
}

canonical_dir() {
    (cd "$1" 2>/dev/null && pwd -P)
}

link_points_to() {
    link_path=$1
    expected_path=$2

    [ -L "$link_path" ] || return 1
    resolved_path=$(canonical_dir "$link_path") || return 1
    [ "$resolved_path" = "$expected_path" ]
}

check_link_destination() {
    link_path=$1
    expected_path=$2

    if [ -e "$link_path" ] || [ -L "$link_path" ]; then
        if ! link_points_to "$link_path" "$expected_path"; then
            echo "error: refusing to replace existing path: $link_path" >&2
            exit 1
        fi
    fi
}

ensure_link() {
    link_path=$1
    expected_path=$2

    if link_points_to "$link_path" "$expected_path"; then
        return
    fi
    mkdir -p "$(dirname "$link_path")"
    ln -s "$expected_path" "$link_path"
}

ensure_exclude_pattern() {
    exclude_file=$1
    pattern=$2

    mkdir -p "$(dirname "$exclude_file")"
    touch "$exclude_file"
    if ! grep -Fqx "$pattern" "$exclude_file"; then
        printf '%s\n' "$pattern" >>"$exclude_file"
    fi
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    usage
    exit 0
fi
if [ "$#" -gt 1 ]; then
    usage >&2
    exit 2
fi

script_dir=$(canonical_dir "$(dirname "$0")")
source_skills=$(canonical_dir "$script_dir/.agents/skills") || {
    echo "error: source skills not found under $script_dir/.agents/skills" >&2
    exit 1
}
workdir=$(canonical_dir "${1:-.}") || {
    echo "error: workdir does not exist: ${1:-.}" >&2
    exit 1
}

git_root=$(git -C "$workdir" rev-parse --show-toplevel 2>/dev/null) || {
    echo "error: workdir is not inside a Git worktree: $workdir" >&2
    exit 1
}
git_root=$(canonical_dir "$git_root")
if [ "$workdir" != "$git_root" ]; then
    echo "error: workdir must be the Git worktree root: $git_root" >&2
    exit 1
fi

if [ "$workdir" = "$script_dir" ]; then
    echo "Skills are already enabled in the playbook repository."
    exit 0
fi

agents_link="$workdir/.agents/skills"
claude_link="$workdir/.claude/skills"

check_link_destination "$agents_link" "$source_skills"
check_link_destination "$claude_link" "$source_skills"
ensure_link "$agents_link" "$source_skills"
ensure_link "$claude_link" "$source_skills"

exclude_file=$(git -C "$workdir" rev-parse --git-path info/exclude)
case "$exclude_file" in
    /*) ;;
    *) exclude_file="$workdir/$exclude_file" ;;
esac
ensure_exclude_pattern "$exclude_file" "/.agents/skills"
ensure_exclude_pattern "$exclude_file" "/.claude/skills"

echo "Enabled playbook skills in $workdir"
echo "  Codex / GitHub Copilot: $agents_link"
echo "  Claude Code:            $claude_link"
echo "  Git-local exclusions:   $exclude_file"
