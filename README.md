# Tugas Sorting & Binary Tree
**Analisis & Desain Algoritma — Bab 12 & Bab 13**

Implementasi lengkap dalam satu file Python: `tugas_sorting_binary_tree.py`

---

## Daftar Isi
1. [Deskripsi Singkat](#deskripsi-singkat)
2. [Persyaratan](#persyaratan)
3. [Cara Menjalankan](#cara-menjalankan)
4. [Struktur Kode](#struktur-kode)
5. [BAB 12 — AdvancedSorter](#bab-12--advancedsorter)
6. [BAB 13 — ExprHeapSorter](#bab-13--exprheapsorter)
7. [Batasan & Persyaratan Teknis](#batasan--persyaratan-teknis)
8. [Kompleksitas Algoritma](#kompleksitas-algoritma)
9. [Contoh Output](#contoh-output)

---

## Deskripsi Singkat

Program ini mengimplementasikan dua modul utama:

| Modul | Kelas | Bab |
|---|---|---|
| Sorting Array & Linked List | `AdvancedSorter` | 12 |
| Expression Tree + Heapsort | `ExprHeapSorter` | 13 |

---

## Persyaratan

- Python **3.8+**
- Tidak memerlukan library eksternal (hanya modul standar: `math`, `typing`, `collections`)

---

## Cara Menjalankan

```bash
python tugas_sorting_binary_tree.py
```

Program akan otomatis menjalankan semua pengujian dan mencetak hasilnya ke terminal.

---

## Struktur Kode

```
tugas_sorting_binary_tree.py
│
├── ListNode                    ← Node untuk Singly Linked List (shared)
├── linked_list_to_list()       ← Helper: linked list → Python list
├── list_to_linked_list()       ← Helper: Python list → linked list
│
├── AdvancedSorter              ← BAB 12
│   ├── sort_array()
│   ├── _rec_merge_sort()
│   ├── _merge_virtual()
│   ├── sort_linked_list()
│   ├── _split_linked_list()
│   ├── _merge_linked_lists()
│   ├── sort_array_quick()
│   ├── _quick_sort_recursive()
│   └── partition_quick()
│
├── ExprHeapSorter              ← BAB 13
│   ├── parse_and_evaluate()
│   ├── _tokenize()
│   ├── _build_tree()
│   ├── _eval_tree()
│   ├── heapsort_inplace()
│   ├── _sift_down()
│   └── is_complete_tree()
│
└── if __name__ == "__main__"   ← Pengujian semua modul
```

---

## BAB 12 — AdvancedSorter

### 1. Array Merge Sort — `sort_array(arr)`

Mengurutkan Python list menggunakan Merge Sort dengan **virtual sublists** dan **satu tmpArray tunggal**.

**Cara kerja:**
- `sort_array()` mengalokasi `tmp_array = [0] * n` **satu kali** di awal.
- `_rec_merge_sort()` membagi array secara rekursif hingga ukuran 1.
- `_merge_virtual()` menggabungkan dua sublist bersebelahan menggunakan `tmp_array` yang sama tanpa alokasi baru.

```python
sorter = AdvancedSorter()
hasil = sorter.sort_array([38, 27, 43, 3, 9, 82, 10])
# → [3, 9, 10, 27, 38, 43, 82]
```

### 2. Linked List Merge Sort — `sort_linked_list(head)`

Mengurutkan Singly Linked List menggunakan Merge Sort tanpa alokasi node baru.

**Teknik yang digunakan:**

| Teknik | Fungsi | Penjelasan |
|---|---|---|
| Fast-Slow Pointer | `_split_linked_list()` | `midPoint` maju 1 langkah, `curNode` maju 2 langkah — menemukan tengah dalam satu traversal |
| Dummy Node + Tail Reference | `_merge_linked_lists()` | Hanya reassign `.next`, tidak ada alokasi node baru |

```python
head = list_to_linked_list([38, 27, 43, 3, 9, 82, 10])
sorted_head = sorter.sort_linked_list(head)
# → [3, 9, 10, 27, 38, 43, 82]
```

### 3. Quick Sort — `sort_array_quick(arr)`

Quick Sort dengan dua mekanisme pengaman:

**Median-of-Three Pivot (`partition_quick`):**
1. Ambil `arr[first]`, `arr[mid]`, `arr[last]`.
2. Urutkan ketiganya via conditional swap → median menjadi pivot.
3. Tukar pivot ke `arr[first]`, jalankan partisi Lomuto.

**Depth Limiter (Fallback ke Merge Sort):**
```
Jika depth > 2 * log2(n)  →  panggil sort_array() untuk subarray tersebut
```
Mencegah kompleksitas O(n²) pada data yang sudah hampir terurut atau terurut terbalik.

```python
hasil = sorter.sort_array_quick([20, 19, 18, ..., 1])
# → [1, 2, 3, ..., 20]  ← tetap O(n log n) meski input descending
```

---

## BAB 13 — ExprHeapSorter

### 4. Expression Tree — `parse_and_evaluate()`

Membangun dan mengevaluasi pohon ekspresi dari string **fully parenthesized**.

**Tata bahasa yang didukung:**
```
expr ::= '(' expr operator expr ')' | number
operator ::= '+' | '-' | '*' | '/'
```

**Contoh:**
```python
ehs = ExprHeapSorter("((8 * 5) + (9 / (7 - 4)))")
ehs.parse_and_evaluate()
# (8*5)=40, (7-4)=3, (9/3)=3, 40+3 = [43]
```

**Penanganan error:**
- Token tidak valid → `ValueError`
- Pembagian dengan nol → `ValueError`
- Tanda kurung tidak seimbang → `ValueError`

**Alur kerja internal:**
```
String → _tokenize() → deque token
                             ↓
                       _build_tree()   ← rekursif, pola Listing 13.9
                             ↓
                        dict tree
                             ↓
                       _eval_tree()    ← postorder traversal
                             ↓
                         nilai int
```

**Mengapa traversal postorder menghasilkan notasi postfix secara otomatis:**
Pada postorder (kiri → kanan → root), operator selalu dicetak setelah kedua operandnya — itulah definisi notasi postfix. Sedangkan inorder memerlukan tanda kurung eksplisit karena operator dicetak di antara operand, sehingga presedensi harus dinyatakan secara eksplisit.

### 5 & 6. Heapsort In-Place — `heapsort_inplace(arr)`

Mengurutkan array ascending menggunakan dua fase:

**Fase 1 — Build Max-Heap (O(n)):**
```
for i in range(n//2 - 1, -1, -1):
    _sift_down(arr, n, i)
```
Mulai dari node internal terbawah naik ke root.

**Fase 2 — Extract & Sort (O(n log n)):**
```
for end in range(n-1, 0, -1):
    swap arr[0] ↔ arr[end]
    _sift_down(arr, end, 0)
```
Nilai terbesar dipindah ke posisi akhir, heap dipulihkan untuk sisa elemen.

**`_sift_down(arr, heap_size, idx)`** menggunakan rumus:
```
left  = 2 * idx + 1
right = 2 * idx + 2
```
Loop selama `largest != idx`, swap dengan anak terbesar, turun ke bawah.

```python
ehs = ExprHeapSorter("...")
hasil = ehs.heapsort_inplace([43, 15, 7, 22, 4, 18, 11, 30])
# → [4, 7, 11, 15, 18, 22, 30, 43]
```

### 7. Complete Tree Validator — `is_complete_tree(arr)`

Memvalidasi apakah array memenuhi properti **complete binary tree** ketika dipetakan ke struktur heap berbasis array.

**Algoritma:**
Setelah pertama kali menemukan node tidak-penuh (hanya punya anak kiri, atau tidak punya anak sama sekali), semua node berikutnya tidak boleh memiliki anak. Bila ada → bukan complete tree.

```python
ehs.is_complete_tree([1, 2, 3, 4, 5, 6, 7])  # → True  (perfect tree)
ehs.is_complete_tree([1, 2, 3, 4, 5, 6])     # → True  (complete)
ehs.is_complete_tree([1, 2, 3, 4, 5])        # → True  (complete)
```

---

## Batasan & Persyaratan Teknis

| # | Batasan | Status |
|---|---|---|
| 1 | Dilarang `list.sort()`, `sorted()`, `heapq`, library eksternal | ✅ |
| 2 | Array Sort: hanya satu `tmp_array` di awal, tidak ada sublist fisik per rekursi | ✅ |
| 3 | Linked List Sort: hanya modifikasi `.next`, satu dummy node per merge | ✅ |
| 4 | Stabilitas wajib (Array & Linked List Merge Sort) | ✅ |
| 5 | Quick Sort fallback ke Merge Sort bila `depth > 2*log2(n)` | ✅ |
| 6 | Heap & Sort benar-benar in-place | ✅ |
| 7 | Penanganan division by zero & token tidak valid | ✅ |
| 8 | Heapsort terminasi tanpa infinite loop | ✅ |

---

## Kompleksitas Algoritma

| Algoritma | Waktu (Average) | Waktu (Worst) | Ruang Tambahan | Stabil |
|---|---|---|---|---|
| Array Merge Sort | O(n log n) | O(n log n) | O(n) — 1 tmpArray | Ya |
| Linked List Merge Sort | O(n log n) | O(n log n) | O(log n) — stack rekursi | Ya |
| Quick Sort (median-of-three) | O(n log n) | O(n log n)* | O(log n) — stack rekursi | Tidak |
| Heapsort In-Place | O(n log n) | O(n log n) | O(1) | Tidak |
| Expression Tree Build | O(n) | O(n) | O(h) — h = tinggi pohon | — |
| Sift-Down | O(log n) | O(log n) | O(1) | — |

> \* Fallback ke Merge Sort bila depth > 2·log₂(n) menjamin tidak ada O(n²).

---

## Contoh Output

```
============================================================
BAB 12 — AdvancedSorter
============================================================

[1] ARRAY MERGE SORT
  Input  : [38, 27, 43, 3, 9, 82, 10]
  Output : [3, 9, 10, 27, 38, 43, 82]
  Stable input  : [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
  Stable output : [1, 1, 2, 3, 3, 4, 5, 5, 6, 9]

[2] LINKED LIST MERGE SORT
  Input  : [38, 27, 43, 3, 9, 82, 10]
  Output : [3, 9, 10, 27, 38, 43, 82]

[3] QUICK SORT (Median-of-Three + Fallback)
  Input           : [38, 27, 43, 3, 9, 82, 10]
  Output          : [3, 9, 10, 27, 38, 43, 82]
  Descending input: [20, 19, 18, ..., 1]
  Output          : [1, 2, 3, ..., 20]

============================================================
BAB 13 — ExprHeapSorter
============================================================

[4] EXPRESSION TREE: ((8 * 5) + (9 / (7 - 4)))
  Hasil: [43]  (manual: (8*5)=40, (7-4)=3, (9/3)=3, 40+3=43)

[5] HEAPSORT IN-PLACE
  Input  : [43, 15, 7, 22, 4, 18, 11, 30]
  Output : [4, 7, 11, 15, 18, 22, 30, 43]

[6] COMPLETE BINARY TREE VALIDATOR
  [OK] 7 node – perfect tree: is_complete=True
  [OK] 6 node – complete: is_complete=True
  [OK] 5 node – complete: is_complete=True

[7] UJI EKSPRESI LAIN & PENANGANAN ERROR
  [OK] ((3 + 4) * (2 - 1)) = 7
  [OK] ((10 / (5 - 5)) + 1) → ERROR: Pembagian dengan nol
  [OK] 5 = 5
```
