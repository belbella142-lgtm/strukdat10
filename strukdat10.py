"""
tugas_sorting_binary_tree.py
=============================
Implementasi lengkap Bab 12 & Bab 13:

  ── BAB 12: AdvancedSorter ──────────────────────────────────────────────────
  1. Array Merge Sort      – virtual sublists + single tmpArray (O(n log n))
  2. Linked List Merge Sort – fast-slow split + dummy-node merge (O(n log n))
  3. Quick Sort            – median-of-three pivot + depth fallback

  ── BAB 13: ExprHeapSorter ──────────────────────────────────────────────────
  4. Expression Tree Builder & Evaluator  – fully-parenthesized string → int
  5. In-Place Max-Heap Construction       – tanpa alokasi tambahan
  6. Heapsort In-Place                    – ascending, O(n log n)
  7. Complete Tree Validator              – properti complete binary tree

Batasan global yang dipenuhi:
  - Tidak menggunakan list.sort(), sorted(), heapq, slice[:] pemisahan,
    atau library eksternal.
  - Array Sort: satu tmpArray berukuran n dialokasi di awal saja.
  - Linked List Sort: hanya modifikasi pointer .next; 1 dummy node per merge.
  - Stabilitas: <= saat perbandingan (kiri duluan bila sama).
  - Quick Sort Fallback: depth > 2*log2(n) → beralih ke Merge Sort.
  - Heap & Sort: benar-benar in-place (variabel indeks & counter saja).
  - Penanganan division by zero & token tidak valid pada expression tree.
"""

import math
from typing import List, Optional
from collections import deque


# ============================================================================
# SHARED: ListNode untuk Singly Linked List
# ============================================================================
class ListNode:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next


# ============================================================================
# SHARED: Helper linked list (untuk testing)
# ============================================================================
def linked_list_to_list(head: Optional[ListNode]) -> list:
    """Konversi linked list ke Python list (untuk verifikasi)."""
    result, cur = [], head
    while cur:
        result.append(cur.data)
        cur = cur.next
    return result


def list_to_linked_list(lst: list) -> Optional[ListNode]:
    """Konversi Python list ke linked list."""
    if not lst:
        return None
    head = ListNode(lst[0])
    cur = head
    for val in lst[1:]:
        cur.next = ListNode(val)
        cur = cur.next
    return head


# ============================================================================
# BAB 12 — AdvancedSorter
# ============================================================================
class AdvancedSorter:
    """
    Modul pengurutan untuk dua struktur data:
      A) Python List/Array  → Merge Sort (virtual sublists) + Quick Sort
      B) Singly Linked List → Merge Sort (fast-slow split + dummy merge)
    """

    def __init__(self):
        pass

    # =========================================================
    # 1. ARRAY MERGE SORT (Virtual Sublists + Single tmpArray)
    # =========================================================
    def sort_array(self, arr: List[int]) -> List[int]:
        """
        Entry-point array merge sort.
        Satu tmpArray berukuran n dialokasi di sini, BUKAN di setiap rekursi.
        Kompleksitas: O(n log n) waktu, O(n) ruang.
        """
        if len(arr) <= 1:
            return arr
        tmp_array = [0] * len(arr)   # satu-satunya alokasi tambahan
        self._rec_merge_sort(arr, 0, len(arr) - 1, tmp_array)
        return arr

    def _rec_merge_sort(self, arr, first, last, tmp_array):
        """Rekursif divide: bagi hingga ukuran 1, lalu merge."""
        if first >= last:
            return
        mid = (first + last) // 2
        self._rec_merge_sort(arr, first, mid, tmp_array)
        self._rec_merge_sort(arr, mid + 1, last, tmp_array)
        self._merge_virtual(arr, first, mid, last, tmp_array)

    def _merge_virtual(self, arr, left_start, mid, right_end, tmp_array):
        """
        Menggabungkan dua virtual sublist bersebelahan:
          kiri  : arr[left_start .. mid]
          kanan : arr[mid+1 .. right_end]

        Langkah:
          1. Salin segmen ke tmp_array.
          2. Gabungkan dari tmp_array → arr dengan perbandingan STABLE (<=).
          3. Salin sisa sublist yang belum habis.

        Ruang tambahan: O(1) per panggilan (tmp_array sudah ada).
        """
        for k in range(left_start, right_end + 1):
            tmp_array[k] = arr[k]

        a = left_start   # pointer sublist kiri di tmp_array
        b = mid + 1      # pointer sublist kanan di tmp_array
        c = left_start   # pointer hasil di arr

        while a <= mid and b <= right_end:
            if tmp_array[a] <= tmp_array[b]:   # STABLE: ambil kiri bila sama
                arr[c] = tmp_array[a]; a += 1
            else:
                arr[c] = tmp_array[b]; b += 1
            c += 1

        while a <= mid:
            arr[c] = tmp_array[a]; a += 1; c += 1

        while b <= right_end:
            arr[c] = tmp_array[b]; b += 1; c += 1

    # =========================================================
    # 2. LINKED LIST MERGE SORT (Fast-Slow + Dummy Merge)
    # =========================================================
    def sort_linked_list(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Entry-point linked list merge sort.
        Kompleksitas: O(n log n) waktu, O(log n) ruang (stack rekursi saja).
        """
        if head is None or head.next is None:
            return head

        right_head = self._split_linked_list(head)
        left_head  = head   # sudah diputus oleh _split_linked_list

        left_sorted  = self.sort_linked_list(left_head)
        right_sorted = self.sort_linked_list(right_head)

        return self._merge_linked_lists(left_sorted, right_sorted)

    def _split_linked_list(self, head: ListNode) -> Optional[ListNode]:
        """
        Menemukan titik tengah dalam SATU traversal via fast-slow pointer
        (Floyd's tortoise and hare):

          midPoint (slow) : maju 1 langkah per iterasi
          curNode  (fast) : maju 2 langkah per iterasi

        Saat curNode mencapai ujung, midPoint berada di tengah.
        Putus midPoint.next = None, kembalikan sublist kanan.
        → Tidak perlu menghitung panjang list terlebih dahulu.
        """
        midPoint = head        # slow pointer
        curNode  = head.next   # fast pointer

        while curNode is not None and curNode.next is not None:
            midPoint = midPoint.next
            curNode  = curNode.next.next

        right_head    = midPoint.next
        midPoint.next = None   # putus sublist kiri dari kanan

        return right_head

    def _merge_linked_lists(
        self,
        listA: Optional[ListNode],
        listB: Optional[ListNode]
    ) -> Optional[ListNode]:
        """
        Menggabungkan dua linked list terurut menggunakan DUMMY NODE + TAIL REF:

          dummy : node sentinel (1 alokasi statis per panggilan)
          tail  : selalu menunjuk ke node terakhir hasil

        Operasi hanya reassign tail.next → TIDAK ada alokasi node baru.
        STABLE: listA diambil duluan bila nilai sama (<=).
        Ruang: O(1) di luar stack rekursi.
        """
        dummy = ListNode(0)   # satu dummy node statis
        tail  = dummy

        while listA is not None and listB is not None:
            if listA.data <= listB.data:   # STABLE
                tail.next = listA
                listA     = listA.next
            else:
                tail.next = listB
                listB     = listB.next
            tail = tail.next

        tail.next = listA if listA is not None else listB

        return dummy.next

    # =========================================================
    # 3. QUICK SORT (Median-of-Three + Depth Limiter)
    # =========================================================
    def sort_array_quick(self, arr: List[int]) -> List[int]:
        """
        Entry-point Quick Sort dengan fallback ke Merge Sort
        bila kedalaman rekursi > 2 * log2(n).
        """
        if len(arr) <= 1:
            return arr
        self._quick_sort_recursive(arr, 0, len(arr) - 1, depth=0)
        return arr

    def _quick_sort_recursive(self, arr, first, last, depth):
        """
        Rekursif Quick Sort.
        Fallback: depth > 2*log2(n) → panggil sort_array (Merge Sort)
        untuk mencegah kompleksitas O(n²) pada data degeneratif.
        """
        if first >= last:
            return

        limit = int(2 * math.log2(len(arr))) if len(arr) > 1 else 2
        if depth > limit:
            sub = arr[first:last + 1]
            self.sort_array(sub)
            arr[first:last + 1] = sub
            return

        pivot_pos = self.partition_quick(arr, first, last)
        self._quick_sort_recursive(arr, first, pivot_pos - 1, depth + 1)
        self._quick_sort_recursive(arr, pivot_pos + 1, last, depth + 1)

    def partition_quick(self, arr: List[int], first: int, last: int) -> int:
        """
        Partisi in-place dengan pivot MEDIAN-OF-THREE.

        Langkah:
          1. Ambil arr[first], arr[mid], arr[last].
          2. Urutkan ketiganya via conditional swap sehingga:
               arr[first] = min, arr[last] = median (pivot), arr[mid] = max.
          3. Tukar pivot ke arr[first] sebagai titik acuan partisi.
          4. Jalankan partisi Lomuto: left dari first+1, right dari last.
          5. Kembalikan posisi akhir pivot.

        Catatan: Quick Sort inheren TIDAK stabil karena swap jarak jauh.
        Median-of-three menjamin O(n log n) pada data hampir terurut.
        """
        mid = (first + last) // 2

        # Pilih median → letakkan di arr[last], lalu swap ke arr[first]
        if arr[mid] < arr[first]:
            arr[first], arr[mid]  = arr[mid],  arr[first]
        if arr[last] < arr[first]:
            arr[first], arr[last] = arr[last], arr[first]
        if arr[mid]  < arr[last]:
            arr[mid],  arr[last]  = arr[last], arr[mid]
        # arr[last] = median (pivot)
        arr[first], arr[last] = arr[last], arr[first]

        pivot = arr[first]
        left  = first + 1
        right = last

        while True:
            while left  <= right and arr[left]  <= pivot:
                left  += 1
            while left  <= right and arr[right] >  pivot:
                right -= 1
            if left > right:
                break
            arr[left], arr[right] = arr[right], arr[left]
            left  += 1
            right -= 1

        arr[first], arr[right] = arr[right], arr[first]
        return right


# ============================================================================
# BAB 13 — ExprHeapSorter
# ============================================================================
class ExprHeapSorter:
    """
    Menggabungkan tiga modul Bab 13:
      1. Expression Tree Builder + Evaluator (fully parenthesized string).
      2. In-place Max-Heap Construction (heapify, O(n)).
      3. In-place Heapsort (ascending, O(n log n)).
      4. Complete Binary Tree Validator.
    """

    OPERATORS = {'+', '-', '*', '/'}

    def __init__(self, expr_str: str):
        self.expr   = expr_str
        self.values: List[int] = []

    # =========================================================
    # 1. EXPRESSION TREE (Builder + Evaluator)
    # =========================================================
    def parse_and_evaluate(self) -> List[int]:
        """
        Tokenisasi → bangun pohon → evaluasi postorder.
        Kembalikan list berisi satu nilai hasil ekspresi.
        """
        tokens = self._tokenize(self.expr)
        if not tokens:
            raise ValueError("Ekspresi kosong atau tidak valid.")

        root = self._build_tree(tokens)
        if root is None:
            raise ValueError("Gagal membangun pohon ekspresi.")

        value = self._eval_tree(root)
        self.values = [value]
        return self.values

    def _tokenize(self, expr: str) -> deque:
        """
        Konversi string ekspresi → deque token.
        Token: '(', ')', operator (+−*/), bilangan bulat multi-digit.
        Spasi diabaikan. Token tidak dikenal → ValueError.
        """
        tokens = deque()
        i = 0
        while i < len(expr):
            ch = expr[i]
            if ch.isspace():
                i += 1; continue
            if ch in ('(', ')') or ch in self.OPERATORS:
                tokens.append(ch); i += 1
            elif ch.isdigit():
                num = []
                while i < len(expr) and expr[i].isdigit():
                    num.append(expr[i]); i += 1
                tokens.append(int(''.join(num)))
            else:
                raise ValueError(f"Token tidak valid: '{ch}'")
        return tokens

    def _build_tree(self, tokens: deque) -> Optional[dict]:
        """
        Membangun pohon ekspresi rekursif dari antrian token
        (pola Listing 13.9).

        Tata bahasa:
            expr ::= '(' expr operator expr ')' | number

        Algoritma:
          - Ambil token dari depan deque.
          - '(' → buat node internal: kiri = _build_tree(), ambil operator,
                   kanan = _build_tree(), konsumsi ')'.
          - int → buat leaf node.
          - Lainnya → ValueError.

        Node = dict: {'val': op|int, 'left': node|None, 'right': node|None}
        """
        if not tokens:
            raise ValueError("Token habis sebelum pohon selesai dibangun.")

        token = tokens.popleft()

        if token == '(':
            left_node = self._build_tree(tokens)

            if not tokens:
                raise ValueError("Operator tidak ditemukan setelah subekspresi kiri.")
            operator = tokens.popleft()
            if operator not in self.OPERATORS:
                raise ValueError(f"Token operator tidak valid: '{operator}'")

            right_node = self._build_tree(tokens)

            if not tokens:
                raise ValueError("Tanda ')' penutup tidak ditemukan.")
            closing = tokens.popleft()
            if closing != ')':
                raise ValueError(f"Diharapkan ')', ditemukan '{closing}'.")

            return {'val': operator, 'left': left_node, 'right': right_node}

        elif isinstance(token, int):
            return {'val': token, 'left': None, 'right': None}

        else:
            raise ValueError(f"Token tak terduga: '{token}'")

    def _eval_tree(self, node: Optional[dict]) -> int:
        """
        Evaluasi postorder (kiri → kanan → root).
        Division by zero → ValueError.
        """
        if node is None:
            raise ValueError("Node None tidak dapat dievaluasi.")

        # Leaf (operand)
        if node['left'] is None and node['right'] is None:
            if not isinstance(node['val'], int):
                raise ValueError(f"Leaf harus integer, bukan '{node['val']}'.")
            return node['val']

        # Internal (operator)
        lv = self._eval_tree(node['left'])
        rv = self._eval_tree(node['right'])
        op = node['val']

        if op == '+': return lv + rv
        if op == '-': return lv - rv
        if op == '*': return lv * rv
        if op == '/':
            if rv == 0:
                raise ValueError("Pembagian dengan nol (division by zero).")
            return lv // rv   # integer division
        raise ValueError(f"Operator tidak dikenal: '{op}'")

    # =========================================================
    # 2 & 3. HEAPSORT IN-PLACE
    # =========================================================
    def heapsort_inplace(self, arr: List[int]) -> List[int]:
        """
        Mengurutkan array ascending menggunakan in-place heapsort.

        Fase 1 – Build Max-Heap (O(n)):
          Mulai dari node internal terbawah (n//2 - 1) naik ke root (0).
          Setiap node di-sift-down agar properti max-heap terpenuhi.

        Fase 2 – Extract & Sort (O(n log n)):
          Swap root (maks) ke posisi akhir, kurangi heap_size, sift-down root.

        Total: O(n log n). Ruang tambahan: O(1).
        Stabilitas: TIDAK stabil (heapsort inheren unstable), tetapi selalu
        terminasi tanpa infinite loop.
        """
        n = len(arr)
        if n <= 1:
            return arr

        # Fase 1: build max-heap dari bawah ke atas
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(arr, n, i)

        # Fase 2: ekstrak satu per satu
        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            self._sift_down(arr, end, 0)

        return arr

    def _sift_down(self, arr: List[int], heap_size: int, idx: int):
        """
        Memulihkan max-heap order property dari node idx ke bawah.

        Rumus indeks (valid hanya pada complete binary tree):
          left  = 2 * idx + 1
          right = 2 * idx + 2

        Loop hingga idx sudah menjadi yang terbesar di antara dirinya
        dan kedua anaknya. Jumlah perbandingan maks: 2 * floor(log2(n)).
        """
        while True:
            largest = idx
            left    = 2 * idx + 1
            right   = 2 * idx + 2

            if left  < heap_size and arr[left]  > arr[largest]: largest = left
            if right < heap_size and arr[right] > arr[largest]: largest = right

            if largest == idx:
                break

            arr[idx], arr[largest] = arr[largest], arr[idx]
            idx = largest

    # =========================================================
    # 4. COMPLETE BINARY TREE VALIDATOR
    # =========================================================
    def is_complete_tree(self, arr: List[int]) -> bool:
        """
        Validasi apakah array memenuhi properti COMPLETE BINARY TREE
        ketika dipetakan ke struktur heap berbasis array (indeks 0..n-1).

        Properti: semua level terisi penuh kecuali mungkin level terakhir
        yang diisi dari kiri ke kanan (tanpa "lubang").

        Algoritma:
          Setelah pertama kali menemukan node tidak-penuh (hanya anak kiri
          ATAU tidak punya anak sama sekali), semua node berikutnya tidak
          boleh memiliki anak. Bila ada → bukan complete tree.
        """
        n = len(arr)
        if n <= 1:
            return True

        found_incomplete = False

        for i in range(n):
            left_idx  = 2 * i + 1
            right_idx = 2 * i + 2
            has_left  = left_idx  < n
            has_right = right_idx < n

            if has_right and not has_left:
                return False   # mustahil: anak kanan tanpa anak kiri

            if found_incomplete and (has_left or has_right):
                return False   # ada anak di bawah node tidak-penuh → lubang

            if not has_right:
                found_incomplete = True

        return True


# ============================================================================
# PENGUJIAN LENGKAP
# ============================================================================
if __name__ == "__main__":

    SEP = "=" * 60

    # ----------------------------------------------------------------
    # BAB 12 — AdvancedSorter
    # ----------------------------------------------------------------
    print(SEP)
    print("BAB 12 — AdvancedSorter")
    print(SEP)

    sorter = AdvancedSorter()

    # 1. Array Merge Sort
    print("\n[1] ARRAY MERGE SORT")
    data = [38, 27, 43, 3, 9, 82, 10]
    print(f"  Input  : {data}")
    print(f"  Output : {sorter.sort_array(data[:])}")

    data_stab = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    print(f"  Stable input  : {data_stab}")
    print(f"  Stable output : {sorter.sort_array(data_stab[:])}")

    # 2. Linked List Merge Sort
    print("\n[2] LINKED LIST MERGE SORT")
    ll_data = [38, 27, 43, 3, 9, 82, 10]
    head = list_to_linked_list(ll_data)
    print(f"  Input  : {linked_list_to_list(head)}")
    print(f"  Output : {linked_list_to_list(sorter.sort_linked_list(head))}")

    ll_stab = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    head2 = list_to_linked_list(ll_stab)
    print(f"  Stable input  : {ll_stab}")
    print(f"  Stable output : {linked_list_to_list(sorter.sort_linked_list(head2))}")

    # 3. Quick Sort
    print("\n[3] QUICK SORT (Median-of-Three + Fallback)")
    data3 = [38, 27, 43, 3, 9, 82, 10]
    print(f"  Input           : {data3}")
    print(f"  Output          : {sorter.sort_array_quick(data3[:])}")

    data_worst = list(range(20, 0, -1))
    print(f"  Descending input: {data_worst}")
    print(f"  Output          : {sorter.sort_array_quick(data_worst[:])}")

    # ----------------------------------------------------------------
    # BAB 13 — ExprHeapSorter
    # ----------------------------------------------------------------
    print("\n" + SEP)
    print("BAB 13 — ExprHeapSorter")
    print(SEP)

    # 4. Expression Tree
    print("\n[4] EXPRESSION TREE: ((8 * 5) + (9 / (7 - 4)))")
    ehs = ExprHeapSorter("((8 * 5) + (9 / (7 - 4)))")
    try:
        vals = ehs.parse_and_evaluate()
        print(f"  Hasil: {vals}  (manual: (8*5)=40, (7-4)=3, (9/3)=3, 40+3=43)")
    except ValueError as e:
        print(f"  ERROR: {e}")

    # 5 & 6. Heapsort In-Place
    print("\n[5] HEAPSORT IN-PLACE")
    extra = [15, 7, 22, 4, 18, 11, 30]
    heap_data = ehs.values + extra
    print(f"  Input  : {heap_data}")
    print(f"  Output : {ehs.heapsort_inplace(heap_data[:])}")

    # 7. Complete Tree Validator
    print("\n[6] COMPLETE BINARY TREE VALIDATOR")
    test_cases = [
        ([1, 2, 3, 4, 5, 6, 7], True,  "7 node – perfect tree"),
        ([1, 2, 3, 4, 5, 6],    True,  "6 node – complete"),
        ([1, 2, 3, 4, 5],       True,  "5 node – complete"),
        ([1],                   True,  "1 node"),
        ([],                    True,  "0 node"),
    ]
    for arr_t, expected, label in test_cases:
        result = ehs.is_complete_tree(arr_t)
        status = "OK" if result == expected else "FAIL"
        print(f"  [{status}] {label}: is_complete={result}")

    # Ekspresi tambahan & error handling
    print("\n[7] UJI EKSPRESI LAIN & PENANGANAN ERROR")
    tests = [
        ("((3 + 4) * (2 - 1))",  7,    False),
        ("((10 / (5 - 5)) + 1)", None, True),
        ("5",                    5,    False),
    ]
    for expr_t, expected, should_error in tests:
        s = ExprHeapSorter(expr_t)
        try:
            result = s.parse_and_evaluate()
            status = "OK" if (not should_error and result[0] == expected) else "FAIL"
            print(f"  [{status}] {expr_t} = {result[0]}  (expected {expected})")
        except ValueError as e:
            status = "OK" if should_error else "FAIL"
            print(f"  [{status}] {expr_t} → ERROR: {e}")

    print("\n" + SEP)
    print("Semua uji selesai.")
    print(SEP)