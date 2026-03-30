<script lang="ts">
  import { getGitDiff, readTextFile, readFileBase64, writeTextFile, listDirectoryectory } from "$lib/api";
  import { fileName as pathFileName } from "$lib/utils/format";
  import { t } from "$lib/i18n/index.svelte";
  import { onMount } from "svelte";
  import { dbg } from "$lib/utils/debug";
  import CodeEditor from "$lib/components/CodeEditor.svelte";
  import MarkdownContent from "$lib/components/MarkdownContent.svelte";
  import FileTreeNode from "$lib/components/FileTreeNode.svelte";

  interface FileNode {
    name: string;
    path: string;
    type: "file" | "directory";
    children?: FileNode[];
    expanded?: boolean;
    depth?: number;
  }

  let { cwd = "" }: { cwd?: string } = $props();

  // ── State ──

  let selectedFilePath = $state("");
  let diffViewFile = $state<string | null>(null);
  let diffViewContent = $state("");
  let diffViewLoading = $state(false);

  let fileContent = $state("");
  let fileLoading = $state(false);
  let fileSaving = $state(false);
  let fileDirty = $state(false);
  let fileError = $state("");
  let activeView = $state<"preview" | "diff">("preview");
  let editorMode = $state<"edit" | "rendered">("edit");

  const PREVIEWABLE_EXTENSIONS = new Set(["md", "markdown"]);
  const IMAGE_EXTENSIONS = new Set([
    "png",
    "jpg",
    "jpeg",
    "gif",
    "svg",
    "webp",
    "ico",
    "bmp",
    "avif",
    "tif",
    "tiff",
    "jfif",
  ]);

  let selectedExt = $derived(selectedFilePath.split(".").pop()?.toLowerCase() ?? "");
  let isPreviewable = $derived(PREVIEWABLE_EXTENSIONS.has(selectedExt));
  let isImage = $derived(IMAGE_EXTENSIONS.has(selectedExt));

  /** Base64 data URL for image preview */
  let imageDataUrl = $state("");

  let projectCwd = $state(cwd);

  // Track original content to detect dirty state
  let originalContent = "";

  // File tree
  let fileTree = $state<FileNode[]>([]);
  let treeLoading = $state(false);

  // ── Diff parsing ──

  interface DiffLine {
    text: string;
    type: "add" | "del" | "context" | "hunk" | "header";
    oldNum: number | null;
    newNum: number | null;
  }

  function parseDiffLines(raw: string): DiffLine[] {
    const result: DiffLine[] = [];
    let oldLine = 0;
    let newLine = 0;
    for (const text of raw.split("\n")) {
      if (text.startsWith("@@")) {
        const match = text.match(/@@ -(\d+)(?:,\d+)? \+(\d+)/);
        if (match) {
          oldLine = parseInt(match[1], 10);
          newLine = parseInt(match[2], 10);
        }
        result.push({ text, type: "hunk", oldNum: null, newNum: null });
      } else if (
        text.startsWith("diff ") ||
        text.startsWith("index ") ||
        text.startsWith("---") ||
        text.startsWith("+++")
      ) {
        result.push({ text, type: "header", oldNum: null, newNum: null });
      } else if (text.startsWith("+")) {
        result.push({ text, type: "add", oldNum: null, newNum: newLine });
        newLine++;
      } else if (text.startsWith("-")) {
        result.push({ text, type: "del", oldNum: oldLine, newNum: null });
        oldLine++;
      } else {
        result.push({ text, type: "context", oldNum: oldLine, newNum: newLine });
        oldLine++;
        newLine++;
      }
    }
    return result;
  }

  // ── File tree ──

  async function loadFileTree(dirPath: string = ""): Promise<FileNode[]> {
    treeLoading = true;
    try {
      const entries = await listDirectory(dirPath || projectCwd, projectCwd);
      const nodes: FileNode[] = [];
      for (const entry of entries) {
        if (entry.name.startsWith(".")) continue; // skip hidden files
        nodes.push({
          name: entry.name,
          path: entry.path,
          type: entry.type,
          expanded: false,
          children: entry.type === "directory" ? [] : undefined,
          depth: 0,
        });
      }
      return nodes;
    } catch (e) {
      dbg("split-view", "Failed to load file tree:", e);
      return [];
    } finally {
      treeLoading = false;
    }
  }

  async function expandDirectory(node: FileNode) {
    if (node.type !== "directory") return;

    node.expanded = !node.expanded;

    if (node.expanded) {
      // Load children if not already loaded
      if (!node.children || node.children.length === 0) {
        try {
          const entries = await listDirectory(node.path, projectCwd);
          node.children = entries
            .filter((e) => !e.name.startsWith("."))
            .map((entry) => ({
              name: entry.name,
              path: entry.path,
              type: entry.type,
              expanded: false,
              children: entry.type === "directory" ? [] : undefined,
              depth: (node.depth || 0) + 1,
            }));
        } catch (e) {
          dbg("split-view", "Failed to expand directory:", e);
          node.expanded = false;
        }
      }
    }
  }

  // ── File preview ──

  async function loadFilePreview(path: string) {
    if (fileDirty && !confirm(t("explorer_discardConfirm"))) return;
    selectedFilePath = path;
    activeView = "preview";
    fileError = "";
    const ext = path.split(".").pop()?.toLowerCase() ?? "";
    editorMode = PREVIEWABLE_EXTENSIONS.has(ext) ? "rendered" : "edit";
    fileLoading = true;
    fileDirty = false;
    imageDataUrl = "";
    try {
      if (IMAGE_EXTENSIONS.has(ext)) {
        const [base64, mime] = await readFileBase64(path, projectCwd);
        imageDataUrl = `data:${mime};base64,${base64}`;
        fileContent = "";
        originalContent = "";
      } else {
        fileContent = await readTextFile(path, projectCwd);
        originalContent = fileContent;
      }
    } catch (e) {
      fileContent = "";
      originalContent = "";
      imageDataUrl = "";
      fileError = String(e);
    } finally {
      fileLoading = false;
    }
  }

  async function saveFile() {
    if (!selectedFilePath || fileSaving || !fileDirty) return;
    fileSaving = true;
    try {
      await writeTextFile(selectedFilePath, fileContent, projectCwd);
      originalContent = fileContent;
      fileDirty = false;
    } catch (e) {
      dbg("split-view", "Save error:", e);
    } finally {
      fileSaving = false;
    }
  }

  // Track dirty state when CodeEditor updates content
  $effect(() => {
    if (!fileLoading) {
      fileDirty = fileContent !== originalContent;
    }
  });

  async function openFileDiff(filePath: string) {
    diffViewFile = filePath;
    activeView = "diff";
    diffViewLoading = true;
    diffViewContent = "";
    try {
      let content = await getGitDiff(projectCwd, false, filePath);
      if (!content.trim()) {
        content = await getGitDiff(projectCwd, true, filePath);
      }
      diffViewContent = content;
    } catch (e) {
      diffViewContent = String(e);
    } finally {
      diffViewLoading = false;
    }
  }

  function closeDiffView() {
    diffViewFile = null;
    diffViewContent = "";
    activeView = "preview";
  }

  function fileName(path: string): string {
    return pathFileName(path);
  }

  // ── Lifecycle ──

  onMount(() => {
    projectCwd = cwd || localStorage.getItem("ocv:project-cwd") || "";

    // Don't load file tree if no project is selected
    if (!projectCwd) {
      fileTree = [];
      treeLoading = false;
    } else {
      loadFileTree().then((nodes) => {
        fileTree = nodes;
      });
    }

    function onProjectChanged(e: Event) {
      const newCwd = (e as CustomEvent).detail?.cwd ?? "";
      if (newCwd && newCwd !== projectCwd) {
        if (fileDirty && !confirm(t("explorer_discardConfirm"))) return;
        projectCwd = newCwd;
        selectedFilePath = "";
        fileContent = "";
        originalContent = "";
        imageDataUrl = "";
        fileDirty = false;
        fileError = "";
        diffViewFile = null;
        diffViewContent = "";
        loadFileTree().then((nodes) => {
          fileTree = nodes;
        });
      }
    }
    window.addEventListener("ocv:project-changed", onProjectChanged);

    return () => {
      window.removeEventListener("ocv:project-changed", onProjectChanged);
    };
  });
</script>

<div class="flex h-full flex-col border-l border-border bg-background">
  <!-- Header -->
  <div class="flex items-center gap-2 border-b border-border px-3 py-2 shrink-0">
    <svg
      class="h-3.5 w-3.5 shrink-0 text-amber-500"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 2H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
    </svg>
    <span class="text-xs font-semibold text-foreground">{t("splitView_files")}</span>
    <span class="flex-1"></span>
    <button
      class="text-muted-foreground hover:text-foreground transition-colors"
      title={t("splitView_refresh")}
      onclick={() => loadFileTree().then((nodes) => (fileTree = nodes))}
    >
      <svg
        class="h-3.5 w-3.5"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
        <path d="M3 3v5h5" />
        <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
        <path d="M16 21h5v-5" />
      </svg>
    </button>
    <button
      class="text-muted-foreground hover:text-destructive transition-colors"
      title={t("splitView_close")}
      aria-label={t("splitView_close")}
      onclick={() => {
        const event = new CustomEvent("ocv:toggle-split-view");
        window.dispatchEvent(event);
      }}
    >
      <svg
        class="h-3.5 w-3.5"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M18 6 6 18" />
        <path d="m6 6 12 12" />
      </svg>
    </button>
  </div>

  <!-- File tree -->
  <div class="flex-1 overflow-y-auto border-b border-border" style="min-height: 150px; max-height: 40%">
    {#if treeLoading}
      <div class="flex items-center justify-center py-4">
        <div
          class="h-4 w-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin"
        ></div>
      </div>
    {:else if fileTree.length === 0}
      <div class="flex items-center justify-center py-8 text-xs text-muted-foreground">
        {t("sidebar_emptyDirectory")}
      </div>
    {:else}
      <div class="py-1">
        {#each fileTree as node (node.path)}
          <FileTreeNode
            {node}
            {selectedFilePath}
            {expandDirectory}
            {loadFilePreview}
          />
        {/each}
      </div>
    {/if}
  </div>

  <!-- File content area -->
  <div class="flex-1 flex flex-col overflow-hidden min-h-0">
    {#if activeView === "diff" && diffViewFile}
      <!-- Diff view header -->
      <div class="flex items-center gap-2 border-b border-border px-3 py-1.5 shrink-0">
        <button
          class="flex h-5 w-5 items-center justify-center rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          onclick={closeDiffView}
          title={t("explorer_closeDiff")}
        >
          <svg
            class="h-3.5 w-3.5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"><path d="m15 18-6-6 6-6" /></svg
          >
        </button>
        <span class="text-xs font-medium text-foreground flex-1 min-w-0 truncate"
          >{diffViewFile}</span
        >
      </div>
      <!-- Diff content -->
      <div class="flex-1 overflow-auto">
        {#if diffViewLoading}
          <div class="flex items-center justify-center py-12">
            <div
              class="h-4 w-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin"
            ></div>
          </div>
        {:else if diffViewContent.trim()}
          {@const diffLines = parseDiffLines(diffViewContent)}
          <table class="w-full text-[10px] font-mono border-collapse">
            {#each diffLines as dl}
              <tr
                class={dl.type === "add"
                  ? "bg-green-500/10"
                  : dl.type === "del"
                    ? "bg-red-500/10"
                    : dl.type === "hunk"
                      ? "bg-blue-500/5"
                      : ""}
              >
                <td
                  class="select-none text-right pr-1 pl-2 text-muted-foreground/40 w-[1%] whitespace-nowrap">{dl.oldNum ?? ""}</td
                >
                <td
                  class="select-none text-right pr-2 text-muted-foreground/40 w-[1%] whitespace-nowrap">{dl.newNum ?? ""}</td
                >
                <td
                  class="whitespace-pre pr-2">{dl.text}</td
                >
              </tr>
            {/each}
          </table>
        {:else}
          <div class="flex flex-col items-center gap-2 py-12 text-center">
            <svg
              class="h-6 w-6 text-muted-foreground/40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"><path d="M20 6 9 17l-5-5" /></svg
            >
            <p class="text-[10px] text-muted-foreground">{t("explorer_noChanges")}</p>
          </div>
        {/if}
      </div>
    {:else if selectedFilePath}
      <!-- File editor header -->
      <div class="flex items-center gap-2 border-b border-border px-3 py-1.5 shrink-0">
        <svg
          class="h-3 w-3 shrink-0 opacity-40"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          ><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" /><path
            d="M14 2v4a2 2 0 0 0 2 2h4"
          /></svg
        >
        <span class="text-xs font-medium text-foreground min-w-0 truncate"
          >{fileName(selectedFilePath)}</span
        >
        {#if fileDirty}
          <span class="h-1.5 w-1.5 rounded-full bg-amber-400 shrink-0" title={t("explorer_modified")}
          ></span>
        {/if}
        <span class="text-[10px] text-muted-foreground truncate flex-1 min-w-0">{selectedFilePath}</span
        >
        {#if isPreviewable && !isImage}
          <div class="flex rounded-md border bg-background p-0.5 shrink-0">
            <button
              class="flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium transition-colors
                {editorMode === 'edit'
                ? 'bg-muted text-foreground'
                : 'text-muted-foreground hover:text-foreground'}"
              onclick={() => (editorMode = "edit")}
            >
              <svg
                class="h-2.5 w-2.5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" /><path
                  d="m15 5 4 4"
                /></svg
              >
            </button>
            <button
              class="flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium transition-colors
                {editorMode === 'rendered'
                ? 'bg-muted text-foreground'
                : 'text-muted-foreground hover:text-foreground'}"
              onclick={() => (editorMode = "rendered")}
            >
              <svg
                class="h-2.5 w-2.5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" /><circle
                  cx="12"
                  cy="12"
                  r="3"
                /></svg
              >
            </button>
          </div>
        {/if}
        {#if !isImage}
          <button
            class="rounded-md px-2 py-0.5 text-[10px] font-medium transition-colors shrink-0 disabled:opacity-40 {fileDirty
              ? 'bg-primary text-primary-foreground hover:bg-primary/90'
              : 'bg-muted text-muted-foreground cursor-default'}"
            disabled={!fileDirty || fileSaving || editorMode === "rendered"}
            title={editorMode === "rendered" ? t("explorer_saveDisabledInPreview") : ""}
            onclick={saveFile}
          >
            {t("common_save")}
          </button>
        {/if}
      </div>
      <!-- File content -->
      <div class="flex-1 overflow-hidden min-h-0">
        {#if fileLoading}
          <div class="flex items-center justify-center py-12">
            <div
              class="h-4 w-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin"
            ></div>
          </div>
        {:else if fileError}
          <div class="flex flex-1 items-center justify-center p-4">
            <p class="text-[10px] text-destructive">{fileError}</p>
          </div>
        {:else if isImage && imageDataUrl}
          <div
            class="flex items-center justify-center h-full overflow-auto p-2 bg-black/5 dark:bg-white/5"
          >
            <img
              src={imageDataUrl}
              alt={fileName(selectedFilePath)}
              class="max-w-full max-h-full object-contain rounded"
            />
          </div>
        {:else if editorMode === "rendered" && isPreviewable}
          <div class="flex-1 overflow-y-auto p-2 h-full text-[11px]">
            {#if fileContent}
              <MarkdownContent
                text={fileContent}
                basePath={selectedFilePath.replace(/[/\\][^/\\]*$/, "")}
              />
            {:else}
              <p class="text-[10px] text-muted-foreground italic">{t("explorer_emptyFile")}</p>
            {/if}
          </div>
        {:else}
          <CodeEditor
            bind:content={fileContent}
            filePath={selectedFilePath}
            onsave={saveFile}
            class="h-full"
          />
        {/if}
      </div>
    {:else}
      <!-- Empty state -->
      <div class="flex flex-1 items-center justify-center">
        <div class="flex flex-col items-center gap-2 text-center">
          <svg
            class="h-8 w-8 text-muted-foreground/20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            ><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" /><path
              d="M14 2v4a2 2 0 0 0 2 2h4"
            /></svg
          >
          <p class="text-[10px] text-muted-foreground">{t("splitView_selectFile")}</p>
        </div>
      </div>
    {/if}
  </div>
</div>
