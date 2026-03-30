<script lang="ts">
  import type { FileNode } from "./SplitViewPanel.svelte";

  let {
    node,
    selectedFilePath,
    expandDirectory,
    loadFilePreview,
  }: {
    node: FileNode;
    selectedFilePath: string;
    expandDirectory: (node: FileNode) => void;
    loadFilePreview: (path: string) => void;
  } = $props();

  let isSelected = $derived(node.path === selectedFilePath);
  let isNotSelected = $derived(!isSelected);
  let depth = $derived(node.depth || 0);
  let paddingLeft = $derived(`${depth * 16 + 8}px`);

  function handleClick() {
    if (node.type === "directory") {
      expandDirectory(node);
    } else {
      loadFilePreview(node.path);
    }
  }

  function handleDoubleClick() {
    if (node.type === "file") {
      loadFilePreview(node.path);
    }
  }
</script>

<div>
  <div
    class="flex items-center gap-1.5 py-1 px-2 cursor-pointer rounded text-xs transition-colors group hover:bg-accent/50"
    class:bg-accent={isSelected}
    style="padding-left: {paddingLeft}"
    onclick={handleClick}
    ondblclick={handleDoubleClick}
    title={node.path}
  >
    {#if node.type === "directory"}
      <svg
        class="h-3.5 w-3.5 shrink-0 transition-transform group-hover:scale-110"
        class:rotate-90={node.expanded}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="m9 18 6-6-6-6" />
      </svg>
    {:else}
      <span class="w-3.5"></span>
    {/if}
    <svg
      class="h-3.5 w-3.5 shrink-0 transition-transform group-hover:scale-105"
      class:text-amber-500={node.type === "directory"}
      class:text-blue-400={node.type === "file"}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      {#if node.type === "directory"}
        <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 2H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
      {:else}
        <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
        <path d="M14 2v4a2 2 0 0 0 2 2h4" />
      {/if}
    </svg>
    <span class="truncate flex-1 min-w-0">{node.name}</span>
    {#if node.type === "directory" && node.children && node.children.length > 0}
      <span class="text-[9px] text-muted-foreground/50 shrink-0">({node.children.length})</span>
    {/if}
  </div>

  {#if node.type === "directory" && node.expanded && node.children}
    <div>
      {#each node.children as child (child.path)}
        <FileTreeNode
          node={child}
          {selectedFilePath}
          {expandDirectory}
          {loadFilePreview}
        />
      {/each}
    </div>
  {/if}
</div>
