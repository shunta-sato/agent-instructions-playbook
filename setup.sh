#!/bin/sh

set -eu

usage() {
    cat <<'EOF'
Usage: ./setup.sh [--overlay] [WORKDIR]

Expose this repository's skills to Codex, GitHub Copilot, and Claude Code in
WORKDIR. WORKDIR defaults to the current directory and must be a Git worktree
root.

By default, setup links each client's entire skills directory to this playbook.
Use --overlay when the target repository must keep its own or third-party skills
alongside playbook skills. Overlay mode creates one symlink per playbook skill
and leaves non-conflicting entries in the target skills directories untouched.
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

check_overlay_parent() {
    parent=$1
    if [ -L "$parent" ]; then
        echo "error: overlay mode requires a real directory, not an existing directory symlink: $parent" >&2
        echo "error: remove the legacy skills-directory symlink before switching this worktree to --overlay" >&2
        exit 1
    fi
    if [ -e "$parent" ] && [ ! -d "$parent" ]; then
        echo "error: overlay skills parent is not a directory: $parent" >&2
        exit 1
    fi
}

overlay_check_all() {
    target_root=$1
    for source_skill in "$source_skills"/*; do
        [ -d "$source_skill" ] || continue
        skill_name=$(basename "$source_skill")
        check_link_destination "$target_root/$skill_name" "$source_skill"
    done
}

overlay_install_all() {
    target_root=$1
    exclude_prefix=$2
    exclude_file=$3

    mkdir -p "$target_root"
    for source_skill in "$source_skills"/*; do
        [ -d "$source_skill" ] || continue
        skill_name=$(basename "$source_skill")
        ensure_link "$target_root/$skill_name" "$source_skill"
        ensure_exclude_pattern "$exclude_file" "$exclude_prefix/$skill_name"
    done
}

overlay=false
workdir_arg=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        --overlay)
            overlay=true
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        --*)
            echo "error: unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [ -n "$workdir_arg" ]; then
                usage >&2
                exit 2
            fi
            workdir_arg=$1
            ;;
    esac
    shift
done

script_dir=$(canonical_dir "$(dirname "$0")")
source_skills=$(canonical_dir "$script_dir/.agents/skills") || {
    echo "error: source skills not found under $script_dir/.agents/skills" >&2
    exit 1
}
workdir=$(canonical_dir "${workdir_arg:-.}") || {
    echo "error: workdir does not exist: ${workdir_arg:-.}" >&2
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

agents_path="$workdir/.agents/skills"
claude_path="$workdir/.claude/skills"

exclude_file=$(git -C "$workdir" rev-parse --git-path info/exclude)
case "$exclude_file" in
    /*) ;;
    *) exclude_file="$workdir/$exclude_file" ;;
esac

if [ "$overlay" = true ]; then
    check_overlay_parent "$agents_path"
    check_overlay_parent "$claude_path"

    # Check both clients completely before mutating either one so name
    # collisions cannot leave a half-installed overlay.
    overlay_check_all "$agents_path"
    overlay_check_all "$claude_path"

    overlay_install_all "$agents_path" "/.agents/skills" "$exclude_file"
    overlay_install_all "$claude_path" "/.claude/skills" "$exclude_file"

    echo "Enabled playbook skills in overlay mode in $workdir"
    echo "  Codex / GitHub Copilot: $agents_path/<skill>"
    echo "  Claude Code:            $claude_path/<skill>"
    echo "  Git-local exclusions:   per playbook skill in $exclude_file"
    exit 0
fi

check_link_destination "$agents_path" "$source_skills"
check_link_destination "$claude_path" "$source_skills"
ensure_link "$agents_path" "$source_skills"
ensure_link "$claude_path" "$source_skills"

ensure_exclude_pattern "$exclude_file" "/.agents/skills"
ensure_exclude_pattern "$exclude_file" "/.claude/skills"

echo "Enabled playbook skills in $workdir"
echo "  Codex / GitHub Copilot: $agents_path"
echo "  Claude Code:            $claude_path"
echo "  Git-local exclusions:   $exclude_file"
