# FlakyFix: Sử dụng các Mô hình Ngôn ngữ Lớn để Dự đoán Thể loại Bản vá và Tự động Sửa mã Kiểm thử Chập chờn (Flaky Tests)

**Tác giả:** Sakina Fatima, Hadi Hemmati, và Lionel C. Briand, Fellow, IEEE  
**Tạp chí:** IEEE Transactions on Software Engineering (TSE), Vol. 50, No. 12, Tháng 12, 2024  
**DOI:** [10.1109/TSE.2024.3472476](https://doi.org/10.1109/TSE.2024.3472476)  
**Ngày nhận bài:** 13 tháng 1, 2024; **Chỉnh sửa:** 30 tháng 8, 2024; **Chấp nhận:** 27 tháng 9, 2024; **Xuất bản:** 2 tháng 10, 2024.

---

### Tóm tắt (Abstract)
Kiểm thử chập chờn (Flaky tests) là một vấn đề nan giải vì chúng pass hoặc fail một cách phi tiền định (non-deterministically) trên cùng một phiên bản phần mềm đang được kiểm thử, gây ra sự hoang mang và lãng phí công sức phát triển. Mặc dù các mô hình học máy đã được ứng dụng để dự đoán tính chập chờn và căn nguyên lỗi của chúng, nhưng có rất ít nghiên cứu tập trung vào việc hỗ trợ sửa chữa vấn đề này. Để giải quyết khoảng trống đó, trong bài báo này, chúng tôi tập trung vào việc dự đoán loại bản vá (fix type) cần thiết để loại bỏ tính chập chờn, và sau đó tiến hành sửa chữa mã kiểm thử dựa trên cơ sở đó. Chúng tôi thực hiện điều này cho một tập con các bài kiểm thử flaky mà căn nguyên của tính chập chờn nằm ngay trong chính mã kiểm thử chứ không phải trong mã nguồn sản phẩm (production code). 

Một ý tưởng cốt lõi là dẫn dắt quy trình sửa chữa bằng tri thức bổ sung về tính chập chờn của bài kiểm thử dưới dạng thể loại bản vá được dự đoán (predicted fix category). Do đó, trước tiên chúng tôi đề xuất một khung làm việc (framework) tự động tạo ra bộ dữ liệu có nhãn cho 13 thể loại bản vá và huấn luyện các mô hình để dự đoán thể loại bản vá của một bài kiểm thử flaky chỉ bằng cách phân tích mã kiểm thử. Kết quả thực nghiệm sử dụng các mô hình mã nguồn (code models) và học ít mẫu (few-shot learning - FSL) cho thấy chúng tôi có thể dự đoán chính xác hầu hết các thể loại bản vá. 

Để chứng minh tính hữu dụng của các nhãn thể loại bản vá này đối với việc tự động sửa chữa tính chập chờn, chúng tôi bổ sung tri thức này vào các câu nhắc (prompts) của GPT-3.5 Turbo – một Mô hình Ngôn ngữ Lớn (LLM) – để yêu cầu các đề xuất sửa chữa. Kết quả cho thấy các nhãn thể loại bản vá được đề xuất, khi kết hợp với học theo ngữ cảnh (in-context learning), giúp nâng cao đáng kể năng lực của GPT-3.5 Turbo trong việc sinh bản vá cho các bài kiểm thử flaky. Dựa trên việc thực thi và phân tích một mẫu các bài kiểm thử flaky được sửa bởi GPT, chúng tôi ước tính rằng một tỷ lệ lớn các bản vá như vậy (khoảng từ 51% đến 83%) được kỳ vọng sẽ pass. Đối với các bài kiểm thử được sửa nhưng vẫn fail, trung bình chỉ cần thay đổi thêm khoảng 16% mã kiểm thử để chúng có thể pass.

**Chỉ số từ khóa (Index Terms):** Kiểm thử chập chờn (Flaky tests), thể loại bản vá (fix category), sửa chữa bài kiểm thử (test repair), mô hình ngôn ngữ lớn (large language models), mô hình mã nguồn (code models), học ít mẫu (few-shot learning), kiểm thử phần mềm (software testing).

---

## I. GIỚI THIỆU (INTRODUCTION)

Kiểm thử chập chờn (Flaky tests) là các ca kiểm thử pass hoặc fail một cách phi tiền định qua các lần chạy khác nhau, mà không hề có bất kỳ sự thay đổi nào trong mã nguồn đang được kiểm thử. Sự bất nhất quán này gây ức chế và rắc rối lớn cho các nhà phát triển cũng như các đội ngũ Đảm bảo Chất lượng (QA), đặc biệt là trong quá trình kiểm thử hồi quy (regression testing). Thông thường, tính chập chờn bắt nguồn từ nhiều yếu tố, bao gồm: sự biến thiên trong các cấu hình dùng để thực thi cùng một đoạn mã, các vấn đề về thời gian/độ trễ (timing issues) chịu ảnh hưởng bởi các lượt thực thi trước đó, hiện tượng tương tranh/chạy đua tiến trình (race conditions) trong các hệ thống đồng thời, và sự thiếu vắng các phụ thuộc bên ngoài.

Flaky test là một vấn đề phổ biến rộng rãi trong phát triển phần mềm và là một thách thức lớn cần giải quyết. Với hàng triệu bài kiểm thử trong các kho chứa (repositories), ngay cả một tỷ lệ nhỏ bài kiểm thử flaky cũng đòi hỏi nỗ lực thủ công khổng lồ để phát hiện và sửa chữa. Ví dụ, một báo cáo từ Google cho thấy trung bình mỗi ngày họ có 1,6 triệu ca kiểm thử bị fail, và 73 nghìn ca trong số đó (chiếm 4,56%) là do các bài kiểm thử flaky gây ra [1], [2]. Nhiều công ty lớn khác như Microsoft [3], Facebook [4], Netflix, Mozilla, và Salesforce [5] cũng đã báo cáo những trải nghiệm tương tự, nơi mà các bài kiểm thử flaky đã làm trì hoãn đáng kể quy trình triển khai sản phẩm của họ.

Theo một nghiên cứu gần đây [6], để phát hiện tính chập chờn của bài kiểm thử, các kỹ sư thực hành hiện vẫn chủ yếu dựa vào việc chạy lại (rerun) và kiểm tra thủ công. Trong các tài liệu nghiên cứu, các công trình tiên tiến nhất (State-of-the-art - SOTA) về xử lý test chập chờn dựa trên cả các kỹ thuật tĩnh [7], [8], [9], [10] và các mô hình học máy (Machine Learning - ML) nâng cao [11], [12], [13], [14], [15], [16], [17], [18], [19] nhằm tự động dự đoán tính chập chờn và các nguyên nhân gây ra nó. Tuy nhiên, có rất ít công trình [20] tập trung vào việc hỗ trợ các nhà phát triển và kiểm thử viên sửa chữa tính chập chờn trong các ca kiểm thử của họ.

Tính chập chờn trong các bài kiểm thử có thể bắt nguồn từ những nguyên nhân vô cùng đa dạng [21] và có thể được giải quyết thông qua nhiều chiến lược khác nhau, như được minh chứng từ Bộ dữ liệu Quốc tế về Kiểm thử Chập chờn (International Dataset of Flaky Tests - IDoFT) [22] – kho lưu trữ mã nguồn mở lớn nhất chứa các bài kiểm thử flaky bằng Java và Python cùng các bản vá tương ứng. Các biện pháp khắc phục trải dài từ việc thay đổi thứ tự thực thi kiểm thử đến việc xử lý các phụ thuộc vào hệ điều hành hoặc phụ thuộc cài đặt thông qua việc chỉnh sửa mã nguồn trong lớp kiểm thử. Nghiên cứu của chúng tôi tập trung vào việc sửa chữa các bài kiểm thử flaky theo phương thức hộp đen (black-box – không cần truy cập vào mã nguồn sản phẩm/production code) bằng cách cập nhật các câu lệnh gây chập chờn ngay trong mã của ca kiểm thử, vốn chiếm 10% (562 bài kiểm thử từ các Pull Request đã được chấp nhận) trong tổng số 5.500 bài kiểm thử thuộc bộ dữ liệu Java [22]. 

Mặc dù các bài kiểm thử flaky này chỉ đại diện cho một phần thiểu số trong tập dữ liệu đó, nhưng các kỹ thuật để sửa chữa chúng là rất cần thiết, qua đó đáp ứng nhu cầu quan trọng của cộng đồng kiểm thử – những người chịu trách nhiệm viết và tiến hóa mã kiểm thử. Ngoài ra, các nghiên cứu như của Akli và cộng sự [23] báo cáo rằng, trong tập dữ liệu của họ, có tới 70% các vấn đề chập chờn bắt nguồn từ chính mã kiểm thử [1], [24], càng củng cố thêm cho trọng tâm nghiên cứu của chúng tôi. 

Sự phân biệt giữa việc sửa mã sản phẩm (production code) và mã kiểm thử (test code) là vô cùng quan trọng:
- Nếu xem xét cả mã sản phẩm, chi phí và độ phức tạp của việc sửa chữa sẽ tăng lên đáng kể, vì nó đòi hỏi phải thu thập dữ liệu độ bao phủ mã (code coverage) trong quá trình thực thi kiểm thử để phục vụ mục đích định vị lỗi (fault localization).
- Điều này đặc biệt thách thức đối với các mã sản phẩm phức tạp có vô số phụ thuộc và thường được viết bằng nhiều ngôn ngữ lập trình khác nhau [12].

Cụ thể hơn, mục tiêu của chúng tôi là:
1. **(a)** Định nghĩa các thể loại bản vá khác nhau được áp dụng cho mã kiểm thử nhằm loại bỏ tính chập chờn;
2. **(b)** Với một ca kiểm thử flaky cho trước (và không có mã sản phẩm), dự đoán thể loại bản vá phù hợp nhất để áp dụng;
3. **(c)** Tích hợp thể loại bản vá được dự đoán này vào một phương pháp tự động sửa chữa bài kiểm thử flaky.

Nghiên cứu của chúng tôi khác biệt với các công trình hiện có [23] vốn chỉ tập trung vào việc dự đoán thể loại của bài kiểm thử flaky dựa trên căn nguyên gốc rễ (root causes) của chúng. Do việc chỉ biết nguyên nhân gốc rễ, đặc biệt là ở mức khái quát cao, không nhất thiết giúp ích cho việc sửa mã kiểm thử, nên công trình của chúng tôi tập trung vào việc dự đoán thể loại bản vá theo khía cạnh: *phần nào của mã kiểm thử cần phải sửa*. Do đó, các thể loại bản vá này được kỳ vọng sẽ định hướng kiểm thử viên hướng tới các sửa đổi cụ thể và từ đó làm giảm công sức điều tra thủ công của họ. Cần lưu ý rằng các thể loại này hữu ích cho cả các nhà phát triển/kiểm thử viên là con người để sửa thủ công tính chập chờn, cũng như cho các công cụ tự động sửa chữa hoàn toàn các ca kiểm thử flaky. Tuy nhiên, trong bài báo này, chúng tôi chỉ báo cáo về khía cạnh sửa chữa tự động.

Để đạt được 3 mục tiêu trên, phương pháp tiếp cận của chúng tôi bao gồm 3 bước:
- **Bước (a):** Phân tích định tính các bộ dữ liệu kiểm thử flaky và đề xuất một danh sách các thể loại bản vá để loại bỏ tính chập chờn của kiểm thử, khi nguyên nhân gốc rễ chỉ nằm trong mã kiểm thử;
- **Bước (b):** Tiến hành các phân tích thực nghiệm để khám phá việc sử dụng các mô hình mã nguồn tiền huấn luyện (pre-trained code models) trong việc dự đoán thể loại bản vá cần thiết nhằm giải quyết các bài kiểm thử flaky đã được xác định;
- **Bước (c):** Đánh giá những cải tiến mà các thể loại này có thể mang lại cho một LLM như GPT khi được yêu cầu sinh các bản vá cho bài kiểm thử flaky.

Trong bước (b), chúng tôi đánh giá hai mô hình mã nguồn nhỏ hơn là **CodeBERT** [25] và **UniXcoder** [26], vốn được thiết kế riêng cho các bộ dữ liệu nhỏ hơn và được tiền huấn luyện với một tập tham số thu gọn (125 triệu tham số). Chúng tôi đã tinh chỉnh (fine-tune) các mô hình này khi có và không có Học ít mẫu (Few-Shot Learning - FSL) [27]. Việc xem xét FSL xuất phát từ thực tế là người ta thường phải đối mặt với các bộ dữ liệu bài kiểm thử flaky nhỏ trong từng thể loại bản vá sẵn có cho quá trình tinh chỉnh.

Trong bước (c), chúng tôi đánh giá hiệu năng của các Mô hình Ngôn ngữ Lớn (LLM) gần đây, cụ thể là **GPT** [28] (với số lượng tham số khổng lồ, lên tới 175 tỷ trong GPT-3.5 Turbo), nhằm phân tích năng lực sinh bản vá cho các bài kiểm thử flaky. Các bước (b) và (c) được minh họa trong **Hình 1**. 

Các phát hiện của chúng tôi chỉ ra một số điểm then chốt:
1. Các mô hình mã nguồn tiền huấn luyện nhỏ thể hiện độ chính xác cao trong việc dự đoán hầu hết các thể loại bản vá, đạt tỷ lệ Precision từ 83% đến 98% và Recall từ 67% đến 97%, chỉ bằng cách phân tích mã kiểm thử;
2. UniXcoder vượt trội hơn CodeBERT trong việc dự đoán các thể loại bản vá;
3. Việc kết hợp FSL không mang lại sự cải thiện đáng kể nào cho kết quả;
4. Các nhãn thể loại bản vá được dự đoán đóng vai trò quan trọng trong việc định hướng GPT sinh ra các bản vá hoàn chỉnh tốt hơn cho bài kiểm thử flaky. Chúng tôi đánh giá điều này bằng độ đo CodeBLEU [29] và đạt điểm trung bình 81% khi sử dụng các nhãn thể loại bản vá dự đoán trong prompt đầu vào, so với 75% khi không có chúng. Các kết quả này tiếp tục được nâng cao hơn nữa nhờ học theo ngữ cảnh (in-context learning) [30], điều mà chúng tôi đã thử nghiệm trên 3 thể loại bản vá khác nhau;
5. Dựa trên việc thực thi và phân tích một mẫu các bài kiểm thử được GPT sửa, chúng tôi ước tính rằng một tỷ lệ lớn có thể kỳ vọng sẽ pass, xấp xỉ trong khoảng từ 46% đến 80%. Đối với các bài kiểm thử được sinh ra nhưng bị fail, các thay đổi cần thiết để sửa chúng là hạn chế, với trung bình 16% số token cần sửa đổi trong mã kiểm thử.

Tóm lại, các đóng góp của bài báo này bao gồm:
- **Định nghĩa một hệ thống phân loại (categorization) cho các bản vá kiểm thử flaky.** Mục tiêu là cung cấp chỉ dẫn thực tế cho việc sửa chữa bài kiểm thử.
- **Phát triển một bộ quy tắc phỏng đoán (heuristics / search rules) và các kịch bản mã nguồn mở đi kèm** để tự động gán nhãn các bài kiểm thử flaky dựa trên bản vá của chúng.
- **Tạo ra một bộ dữ liệu công khai gồm các bài kiểm thử flaky đã được gán nhãn** phục vụ huấn luyện, sử dụng kịch bản tự động của chúng tôi.
- **Định nghĩa một khung làm việc hộp đen (black-box framework) để dự đoán thể loại bản vá kiểm thử flaky** sử dụng các mô hình mã nguồn (mô hình ngôn ngữ tiền huấn luyện trên code) và học ít mẫu.
- **Phân tích định lượng và định tính hai mô hình mã nguồn nhỏ SOTA**, có và không có FSL, để so sánh các mô hình dự đoán thay thế.
- **Tự động sinh bản vá cho các bài kiểm thử flaky bằng LLM (GPT-3.5 Turbo)**, có và không có các thể loại bản vá dự đoán, nhằm phân tích cách các nhãn này nâng cao chất lượng bản vá được sinh ra.
- **Dựa trên việc thực thi một mẫu các bài kiểm thử do GPT sinh ra**, chúng tôi dựa vào số liệu CodeBLEU và các phương pháp thống kê, bao gồm bootstrapping và hồi quy logistic (logistic regression), để ước tính tỷ lệ pass cho tất cả các bài kiểm thử được sửa (kể cả những bài không thể thực thi được trong môi trường cục bộ). Chúng tôi cũng đánh giá khối lượng sửa đổi cần thiết để sửa thủ công các bài test bị fail.

Phần còn lại của bài báo được tổ chức như sau: 
- **Mục II** trình bày phương pháp tiếp cận của chúng tôi để phát triển công cụ tự động gán nhãn bài kiểm thử flaky với các thể loại bản vá và dự đoán các thể loại đó bằng mô hình mã nguồn, có và không có FSL; đồng thời mô tả cách tích hợp các nhãn này vào prompt của GPT để tạo cơ chế tự động sửa lỗi hoàn toàn.
- **Mục III** đánh giá phương pháp, báo cáo kết quả thực nghiệm và thảo luận về các hàm ý của chúng.
- **Mục IV** báo cáo phân tích định tính về hai mô hình mã nguồn nhỏ và LLM để chứng minh và giải thích khả năng học từ mã kiểm thử cũng như việc đưa ra dự đoán và sinh bản vá.
- **Mục V** phân tích các mối đe dọa đối với tính hợp lệ của nghiên cứu.
- **Mục VI** rà soát và đối chiếu với các công trình liên quan.
- **Mục VII** kết luận bài báo và gợi mở các hướng nghiên cứu tương lai.


---

## II. PHƯƠNG PHÁP TIẾP CẬN (APPROACH)

Phương pháp tiếp cận của bài báo này được chia thành ba giai đoạn chính (được minh họa tổng quan trong **Hình 1**):
- **(a)** Tự động xây dựng một bộ dữ liệu chất lượng cao về các thể loại bản vá, dựa trên các tập dữ liệu hiện có về các ca kiểm thử flaky và các bản vá của chúng;
- **(b)** Xây dựng một mô hình dự đoán thể loại bản vá, sử dụng bộ dữ liệu vừa tạo ra, để định hướng quá trình sửa chữa bài kiểm thử flaky;
- **(c)** Tự động sinh phiên bản đã sửa lỗi của một bài kiểm thử flaky cho trước bằng cách sử dụng các LLM, với sự hỗ trợ từ các thể loại bản vá được dự đoán của chúng tôi.

```
+-------------------------------------------------------------------------------------------------------+
| Hình 1: Quy trình dự đoán nhãn thể loại bản vá và sinh mã kiểm thử flaky đã sửa bằng mô hình ngôn ngữ lớn|
|                                                                                                       |
|  [Mã kiểm thử Flaky] ---> [Mô hình Code (CodeBERT/UniXcoder)] ---> [Dự đoán Thể loại Bản vá]          |
|                                                                               |                       |
|                                                                               v                       |
|  [Mã kiểm thử Flaky] -----------------------------------------------> [Prompt nạp GPT-3.5]            |
|                                                                               |                       |
|                                                                               v                       |
|                                                                    [Mã Kiểm thử Đã Sửa lỗi]           |
+-------------------------------------------------------------------------------------------------------+
```

---

### A. Tự động Xây dựng Bộ Dữ liệu các Thể loại Bản vá (Automatically Constructing a Dataset of Fix Categories)

Việc sở hữu một phương pháp luận phù hợp và được định nghĩa chặt chẽ để xây dựng bộ dữ liệu chất lượng cao về các thể loại bản vá có ý nghĩa quan trọng trong thực tiễn, bởi chúng tôi dự đoán rằng trong hầu hết các bối cảnh phát triển, các mô hình dự đoán cục bộ sẽ cần được xây dựng dựa trên dữ liệu thu thập tại chỗ. 

Tóm lại, phương pháp của chúng tôi bắt đầu từ một tập hợp các thể loại bản vá sẵn có, sau đó mở rộng thành một tập hợp toàn diện và mang tính thực tiễn hơn, và cuối cùng thiết kế các luật phỏng đoán (heuristics) để tự động gán nhãn các bản vá trong các tập dữ liệu kiểm thử flaky hiện có.

Theo hiểu biết tốt nhất của chúng tôi, các thể loại bản vá kiểm thử flaky do Parry và cộng sự [20] trình bày (**Bảng I**) đại diện cho phân loại lớn nhất và gần đây nhất trong y văn. Các thể loại bản vá này đã được các tác giả đánh giá thủ công thông qua việc phân tích mã diff, bình luận của lập trình viên và các issue liên kết của 75 commit sửa lỗi chập chờn bắt nguồn từ 31 dự án Python mã nguồn mở [20].

#### BẢNG I: PHÂN BỐ CÁC BÀI KIỂM THỬ FLAKY THEO NGUYÊN NHÂN VÀ BẢN VÁ CỦA LẬP TRÌNH VIÊN (PARRY ET AL. [20])
*Mỗi bài kiểm thử flaky được gán một thể loại mô tả nguyên nhân chập chờn (các hàng) và một thể loại mô tả bản vá do lập trình viên áp dụng (các cột).*

| Nguyên nhân (Cause) | Add Mock | Add/Adjust Wait | Guarantee Order | Isolate State | Manage Resource | Reduce Random | Reduce Scope | Widen Assertions | Miscellaneous | Tổng cộng |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Async. Wait** | 1 | 6 | - | - | - | - | - | 2 | - | **9** |
| **Concurrency** | - | 2 | - | - | 2 | - | - | 2 | 2 | **8** |
| **Floating Point** | - | - | - | - | - | - | - | 3 | - | **3** |
| **I/O** | - | - | - | - | - | - | - | - | - | **0** |
| **Network** | 3 | 3 | - | - | 1 | - | - | - | 1 | **8** |
| **Order Dependency** | - | - | - | 2 | - | - | 1 | - | - | **3** |
| **Randomness** | - | - | - | - | - | 6 | - | 4 | 1 | **11** |
| **Resource Leak** | - | - | - | - | 2 | - | 1 | 1 | - | **4** |
| **Time** | 5 | - | - | - | - | - | 1 | 1 | 2 | **9** |
| **Unordered Coll.** | - | - | 3 | - | - | - | - | - | - | **3** |
| **Miscellaneous** | 2 | - | 1 | - | 1 | - | - | 6 | 7 | **17** |
| **Tổng cộng** | **11** | **11** | **4** | **2** | **6** | **6** | **3** | **19** | **13** | **75** |

Quy trình phân loại của họ tiếp nhận nhiều nguồn thông tin (tức là không chỉ bản vá mà còn cả bình luận và issue liên kết) để gắn kết một bài kiểm thử flaky với một thể loại bản vá. Thông tin này có thể không hoàn toàn sẵn có đối với nhiều bài kiểm thử flaky trong một dự án. Do đó, theo quy trình đó, không phải tất cả các bản vá đều có thể được gán nhãn nếu chúng ta chỉ có quyền truy cập vào các bài kiểm thử flaky và bản vá của chúng – vốn là trường hợp phổ biến của nhiều bộ dữ liệu.

Trong bài báo này, chúng tôi hướng tới việc phân loại các bản vá và huấn luyện một mô hình dự đoán với mục tiêu: **gán một thể loại bản vá cho một bài kiểm thử flaky mới mà không cần bất kỳ thông tin nào khác ngoài chính mã nguồn của ca kiểm thử đó**. Nói cách khác, mục tiêu là định hướng các kiểm thử viên (hoặc các công cụ sửa chữa tự động) áp dụng đúng bản vá dựa trên các thể loại bản vá có thể dự đoán được chỉ từ mã kiểm thử. 

Mặc dù không phải mọi bài kiểm thử flaky đều có thể giải quyết duy nhất bằng cách can thiệp vào mã kiểm thử, nhưng một tập con thực sự có thể được sửa theo cách này. Tự động hóa các bản vá này vẫn giúp tiết kiệm đáng kể thời gian và tài nguyên. Vì vậy, việc tạo lập dữ liệu của chúng tôi nhắm vào các bản vá cụ thể này. Để đạt được điều đó, chúng tôi đã phân tích các ca kiểm thử flaky và bản vá của chúng để trích xuất nhãn chân lý (ground truth). Lấy cảm hứng từ công trình của Parry và cộng sự [20], chúng tôi phân tích **Tập dữ liệu Quốc tế về Kiểm thử Chập chờn (IDoFT)** [^1], bao gồm các ca kiểm thử flaky cùng bản vá từ 123 dự án Java mã nguồn mở.

[^1]: Kho lưu trữ IDoFT: `https://mir.cs.illinois.edu/flakytests`

Bộ dữ liệu này, vốn đã được sử dụng trong nhiều nghiên cứu trước đây về dự đoán ca kiểm thử flaky [5], [12], [31], [32], [33], [34], [35], là một tập dữ liệu công khai và được cập nhật thường xuyên. Chúng tôi đảm bảo việc sử dụng phiên bản mới nhất của bộ dữ liệu này.

Để gán nhãn thể loại bản vá cho bộ dữ liệu IDoFT, hai nghiên cứu viên đã phân tích độc lập và thủ công 100 bài kiểm thử flaky được chọn ngẫu nhiên cùng các bản vá tương ứng để ánh xạ chúng vào một hoặc nhiều thể loại do Parry và cộng sự đề xuất (**Bảng I**) hoặc tạo ra một thể loại mới khi bản vá không khớp với bất kỳ thể loại nào trước đó. Các thể loại mới phải thỏa mãn: vừa có thể dự đoán được chỉ bằng cách nhìn vào bài kiểm thử flaky, vừa đủ hữu ích để giúp các nhà phát triển và kiểm thử viên sửa chữa chúng. 

Các bất đồng về thể loại và định nghĩa giữa hai nghiên cứu viên được giải quyết thông qua nhiều cuộc họp thảo luận. Chúng tôi sử dụng hệ số Cohen's Kappa [36] để đo lường mức độ đồng thuận ban đầu giữa hai nghiên cứu viên (sẽ thảo luận ngắn gọn ở Mục III). Không có trường hợp nào cần đến ý kiến của người thứ ba để giải quyết mâu thuẫn.

Một số thể loại bản vá do Parry và cộng sự đề xuất cũng được đổi tên trong nghiên cứu của chúng tôi để tăng tính dễ hiểu. Ví dụ: thuật ngữ *Reduce Scope* (một trong các thể loại của Parry et al.) thiếu sự rõ ràng trong việc chỉ ra chính xác phần mã nào cần chỉnh sửa. Bằng cách đổi tên *Reduce Scope* thành **Change Condition**, các nhà phát triển và kiểm thử viên được hướng dẫn rõ ràng hơn về việc phải chỉnh sửa các câu lệnh điều kiện. 

Quy trình này đã mang lại **13 thể loại bản vá khác nhau** cho các bài kiểm thử flaky, được trình bày trong **Bảng II**.

#### BẢNG II: SỐ LƯỢNG BÀI KIỂM THỬ FLAKY TRONG TỪNG THỂ LOẠI BẢN VÁ (SỬ DỤNG GÁN NHÃN TỰ ĐỘNG)
*Các thể loại có trên 30 thực thể được in đậm/nổi bật để phục vụ huấn luyện mô hình.*

| Thể loại Bản vá Kiểm thử Flaky (Flaky Test Fix Category) | Số lượng Bài kiểm thử Flaky |
|---|:---:|
| **Change Assertion** (Thay đổi mệnh đề khẳng định) | **197** |
| **Change Condition** (Thay đổi câu lệnh điều kiện) | **121** |
| **Reset Variable** (Thiết lập lại biến/trạng thái) | **104** |
| **Reorder Data** (Sắp xếp lại dữ liệu) | **92** |
| **Change Data Structure** (Thay đổi cấu trúc dữ liệu) | **91** |
| **Handle Exception** (Xử lý ngoại lệ) | **52** |
| **Miscellaneous** (Hỗn hợp / Khác) | **50** |
| **Change Data Format** (Thay đổi định dạng dữ liệu) | **46** |
| **Reorder Parameters** (Đổi thứ tự tham số) | **37** |
| Call Static Method (Gọi phương thức tĩnh) | 9 |
| String Matching (Khớp chuỗi) | 6 |
| Change Timezone (Thay đổi múi giờ) | 3 |
| Handle Timeout (Xử lý thời gian chờ) | 2 |

Bước cuối cùng trong giai đoạn này là xây dựng một bộ các quy tắc phỏng đoán (heuristics) để tự động gán nhãn từng bản vá từ bộ dữ liệu của chúng tôi vào một trong 13 thể loại này. Mỗi heuristic là một quy tắc tìm kiếm (được hiện thực hóa dưới dạng một kịch bản Python) dựa trên các từ khóa từ mã diff giữa ca kiểm thử flaky và phiên bản đã sửa của nó. Tiếp theo, chúng tôi xác minh thủ công các đầu ra của quy trình gán nhãn tự động để đảm bảo tính chính xác của các heuristic cho các bộ dữ liệu tương lai. Toàn bộ quy trình gán nhãn được minh họa trong **Hình 2**. 

Sau bước cuối này, 462 bài kiểm thử còn lại trong bộ dữ liệu của chúng tôi đã được gán nhãn tự động bằng các heuristic vừa phát triển. Cần lưu ý rằng một bài kiểm thử đơn lẻ có thể được gán nhiều nhãn thể loại bản vá khác nhau, như thể hiện trong Bảng II.

Dưới đây, chúng tôi giải thích ngắn gọn heuristic của từng thể loại cùng một số ví dụ trích từ bộ dữ liệu IDoFT:

1. **Change Assertion:** Heuristic tìm kiếm từ khóa `assert` và các thành phần thay thế của nó trong mã kiểm thử đã sửa. Ví dụ: nếu `AssertEquals`, `AssertThat`, hoặc `AssertTrue` xuất hiện trong các dòng bị xóa, và `AssertJsonStringEquals`, `assertJSONEqual`, `AssertJsonEqualsNonStrict`, hoặc `JsonAssert.AssertEquals` xuất hiện trong các dòng được thêm vào, điều đó phản ánh sự thay đổi khẳng định để xử lý tính chập chờn. Một trường hợp chập chờn phổ biến phát sinh do sử dụng sai loại assertion. Ví dụ: nên dùng `assertJSONEqual` thay cho `AssertThat` trong một hàm assert lấy đối tượng JSON từ các hàm khác trong mã test và so sánh nó với một chuỗi JSON cứng để đảm bảo thứ tự tiền định của đối tượng JSON được lấy về (Ví dụ: PR vjtools #168 [^2]).
2. **Change Data Structure:** Thay đổi cấu trúc dữ liệu có thể là một kỹ thuật hiệu quả để cải thiện độ tin cậy của kiểm thử và giảm tính chập chờn [37], [38]. Ví dụ: các cấu trúc dữ liệu `HashMap`, `Set`, và `HashSet` là các tập hợp không có thứ tự (unordered collections). Việc sử dụng chúng trong mã kiểm thử có thể dẫn đến flaky nếu bài test phụ thuộc vào thứ tự của các phần tử. Trong các trường hợp đó, các cấu trúc dữ liệu này nên được thay thế tương ứng bằng `LinkedHashMap`, `LinkedMap`, `LinkedSet`, hoặc `LinkedHashSet`, vì chúng duy trì thứ tự lưu trữ các phần tử bất kể bài test được thực thi bao nhiêu lần. Nếu các từ khóa `Hash`, `Map`, `Set`, `HashMap`, `HashSet` được thay thế trong diff bằng các cấu trúc `Linked*`, bài test sẽ được gán nhãn **Change Data Structure** (Ví dụ: PR biojava #897 [^3]).
3. **Handle Exception:** Xử lý ngoại lệ là công cụ quan trọng để giảm thiểu các hành vi ngoài ý muốn do đầu vào hoặc kịch bản sai. Nếu các câu lệnh `try-catch` được thêm vào hoặc loại bỏ, hoặc có sự thay đổi trong kiểu `Exception` được sử dụng, bài test được gán nhãn **Handle Exception** (Ví dụ: PR incubator #398 [^4], PR vjtools #168 [^5]).
4. **Reset Variable:** Một bài test flaky được gán nhãn **Reset Variable** nếu một trong các từ khóa `reset`, `clear`, `remove`, hoặc `purge` xuất hiện trong diff. Đây là các lệnh hữu ích để tái lập trạng thái hệ thống và dọn sạch bộ nhớ ở cuối ca kiểm thử, đưa hệ thống về trạng thái ban đầu để tránh gây ảnh hưởng sang bài test khác (Ví dụ: PR nifi #6754 [^6]).
5. **Change Data Format:** Sự không khớp định dạng đầu vào có thể gây chập chờn. Đôi khi bản vá chỉ đơn giản là đổi định dạng của biến đầu vào sang định dạng yêu cầu. Nếu có sự thay đổi trong định dạng chuỗi hoặc dữ liệu số được dùng trong một hàm của mã test, ca kiểm thử được gán nhãn **Change Data Format**.
6. **Change Condition:** Nếu các câu lệnh điều kiện được thêm hoặc bớt trong mã test, ví dụ thay thế từ khóa `containsexactly` bằng `containsexactlyinanyorder`, bài test được gán nhãn **Change Condition** (Ví dụ: PR servicecomb-java-chassis #3393 [^7]).
7. **Reorder Data:** Nếu xuất hiện bất kỳ từ khóa nào như `sortfield`, `sort_properties`, `sorted`, `order by`, hoặc `sort` trong mã test đã sửa nhằm sắp xếp hoặc thay đổi thứ tự dữ liệu, bài test được gán nhãn **Reorder Data** (Ví dụ: PR common-kafka #50 [^8]).
8. **Reorder Parameters:** Nếu có sự thay đổi về thứ tự các tham số truyền vào hàm, nhãn **Reorder Parameters** sẽ được áp dụng (Ví dụ: PR nifi #6709 [^9]).
9. **Change Time Zone:** Các bài test có thể dựa vào ngày hoặc giờ cụ thể, vốn có thể bị ảnh hưởng bởi sự khác biệt múi giờ. Thiết lập một múi giờ cụ thể giúp đảm bảo kết quả nhất quán [1], [39]. Nếu có sự thay đổi giá trị gán cho từ khóa `timezone`, bài test được gán nhãn **Change Time Zone**.
10. **Handle Timeout:** Nếu từ khóa `timeout` được thêm vào mã test để đảm bảo bài test hoàn thành trong một khung thời gian hợp lý, bài test được gán nhãn **Handle Timeout** (theo đề xuất của Pei et al. [40] để sửa flaky liên quan đến Async Wait).
11. **Call Static Method:** Phương thức tĩnh có thể giúp đảm bảo hành vi kiểm thử nhất quán bằng cách đóng gói các kịch bản phức tạp hoặc giả lập hành vi (như mô phỏng lỗi mạng hoặc độ trễ thời gian). Nếu một lời gọi phương thức tĩnh được thêm vào, test được gán nhãn **Call Static Method**.
12. **String Matching:** Nếu hai chuỗi được so khớp trong bài test để đảm bảo chúng đúng thứ tự nhằm duy trì tính tiền định bằng các từ khóa như `match.that(s).isequalto` hoặc `.matches`, bài test được gán nhãn **String Matching** (Ví dụ: PR immutables #1350 [^10]).
13. **Miscellaneous:** Cuối cùng, nếu có sự thay đổi trong các dòng mã được thêm hoặc xóa mà không thuộc bất kỳ thể loại nào nêu trên, bài test được gán nhãn **Miscellaneous** (Ví dụ: PR emobility-smart-charging #42 [^11], PR sofa-boot #1124 [^12]).

[^2]: `https://github.com/vipshop/vjtools/pull/168`
[^3]: `https://github.com/biojava/biojava/pull/897`
[^4]: `https://github.com/apache/incubator/pull/398`
[^5]: `https://github.com/vipshop/vjtools/pull/168/files`
[^6]: `https://github.com/apache/nifi/pull/6754`
[^7]: `https://github.com/apache/servicecomb-java-chassis/pull/3393`
[^8]: `https://github.com/cerner/common-kafka/pull/50`
[^9]: `https://github.com/apache/nifi/pull/6709/files`
[^10]: `https://github.com/immutables/immutables/pull/1350`
[^11]: `https://github.com/emobility-smart-charging/pull/42`
[^12]: `https://github.com/sofastack/sofa-boot/pull/1124`

---

### B. Dự đoán Thể loại Bản vá của Ca Kiểm thử Flaky bằng các Mô hình Mã nguồn (Flaky Test Case Fix Category Prediction With Code Models)

Trong phần này, chúng tôi mô tả cách sử dụng các mô hình ngôn ngữ khác nhau để dự đoán thể loại bản vá của một bài kiểm thử flaky. Dự đoán này không chỉ hữu ích trong việc giúp kiểm thử viên nhận diện bản vá cần thiết mà còn có thể định hướng bất kỳ quy trình sửa chữa tự động nào.

Chúng tôi sử dụng hai mô hình mã nguồn khác nhau là **CodeBERT** [25] và **UniXcoder** [26] làm các mô hình dự đoán. Nhìn chung, các mô hình ngôn ngữ được tiền huấn luyện bằng phương pháp học tự giám sát (self-supervised learning) trên một kho ngữ liệu khổng lồ không có nhãn. Sau đó, chúng được tinh chỉnh (fine-tuned) bằng một tập dữ liệu cụ thể có nhãn cho các tác vụ Xử lý Ngôn ngữ Tự nhiên (NLP) khác nhau như phân loại văn bản, trích xuất quan hệ hoặc dự đoán câu tiếp theo [25]. 

Mô hình mã nguồn (code models) là các mô hình ngôn ngữ được tiền huấn luyện chuyên biệt trên các ngôn ngữ lập trình. CodeBERT và UniXcoder đã được tiền huấn luyện trên kho ngữ liệu đa dạng bao gồm mã nguồn từ 6 ngôn ngữ lập trình: Java, Python, JavaScript, PHP, Ruby, và Go. Cả hai mô hình đều xuất sắc trong các tác vụ phân loại mã nguồn so với các mô hình khác [12], [41]. Chúng thấu hiểu cả cú pháp và ngữ nghĩa của nhiều ngôn ngữ lập trình. 

Chúng tôi tinh chỉnh độc lập các mô hình mã nguồn này trên tập dữ liệu kiểm thử flaky của mình để học các mẫu hình tiềm ẩn gây ra tính chập chờn của mã kiểm thử. Trong giai đoạn suy diễn (inference), các mô hình đã tinh chỉnh này sẽ phân loại các bài kiểm thử flaky dựa trên những gì chúng đã học được. 

Chúng tôi **chủ động chọn không tinh chỉnh các Mô hình Ngôn ngữ Lớn (LLMs) như GPT hay CodeLlama** cho tác vụ dự đoán thể loại bản vá vì:
1. Chi phí tinh chỉnh các LLM là cực kỳ tốn kém và đòi hỏi lượng dữ liệu khổng lồ cùng tài nguyên tính toán rất lớn [42];
2. Các kết quả thực nghiệm sẽ chỉ ra rằng các mô hình mã nguồn nhỏ hơn đã mang lại độ chính xác rất cao, khiến việc chuyển sang các mô hình phức tạp và nặng nề hơn trở nên không cần thiết;
3. Các mô hình nhỏ làm việc rất tốt trong việc phân loại code [41], hiệu quả về mặt chi phí, tốn ít thời gian và tài nguyên tính toán, khiến chúng mang tính thực tiễn cao hơn nhiều khi tích hợp vào các hệ thống công nghiệp quy mô lớn.

Để tinh chỉnh CodeBERT và UniXcoder dự đoán thể loại bản vá, chúng tôi áp dụng hai kỹ thuật khác nhau:
- **Kỹ thuật 1: Học ít mẫu (Few-Shot Learning - FSL) kết hợp Mạng Siamese (Siamese Network):** Nhằm giải quyết tình trạng tập dữ liệu nhỏ trong bối cảnh phát triển điển hình. Khác với FlakyCat [23] (vốn cũng dùng FSL), chúng tôi huấn luyện mô hình trên tập dữ liệu được xây dựng theo quy trình ở Mục II-A, trong đó mỗi phần tử dữ liệu là một cặp gồm ca kiểm thử flaky và thể loại bản vá của nó. Lưu ý rằng chúng tôi **không sử dụng thông tin từ bản vá thực tế trong thời gian suy diễn**, vì mục tiêu là dự đoán thể loại bản vá cho một bài test flaky chưa được sửa (trong thực tế, mô hình chỉ nhìn thấy mã kiểm thử).
- **Kỹ thuật 2: Mạng Nơ-ron Truyền thẳng (Feed Forward Neural Network - FNN):** Tinh chỉnh mô hình bằng một mạng FNN đơn giản gắn phía sau, tương tự như các công trình phân loại flaky test trước đây như Flakify [12].

Ngoài ra, chúng tôi **không xây dựng một mô hình phân loại đa lớp (multi-class)** duy nhất, mà **xây dựng nhiều mô hình phân loại nhị phân (multiple binary classification models)** để ước lượng xác suất một bài test có thuộc về từng thể loại hay không. Lý do là vì một bài kiểm thử flaky có thể đồng thời thuộc về nhiều thể loại bản vá khác nhau. Với các bộ phân loại nhị phân độc lập, mỗi thể loại bản vá được đối xử riêng biệt, cho phép mô hình học các đặc trưng liên quan nhất cho thể loại đó. Do bộ dữ liệu tương đối nhỏ, việc xây dựng nhiều bộ phân loại nhị phân không gây tốn kém chi phí tính toán.

#### 1) Chuyển đổi Mã Kiểm thử thành Biểu diễn Vector (Converting Test Code to Vector Representation)
Dự đoán bằng mô hình ngôn ngữ bắt đầu bằng việc mã hóa đầu vào vào không gian vector. Trong trường hợp của chúng tôi, các ca kiểm thử được nhúng vào không gian vector phù hợp bằng CodeBERT và UniXcoder.

Cả CodeBERT và UniXcoder tiếp nhận mã của ca kiểm thử làm đầu vào và chuyển đổi nó thành một chuỗi các token. Các token này sau đó được chuyển thành biểu diễn vector số nguyên (embeddings). Mã kiểm thử được phân tách token bằng thuật toán mã hóa cặp byte (Byte-Pair Encoding - BPE) [43], chia nhỏ các từ thành chuỗi các từ con (sub-words). Mỗi token sau đó được ánh xạ vào một chỉ mục dựa trên vị trí và ngữ cảnh. Các chỉ mục này được đưa vào mô hình CodeBERT / UniXcoder để sinh ra một biểu diễn vector cho từng token. Cuối cùng, đối với một ca kiểm thử, tất cả các vector token được tổng hợp lại để tạo thành một vector đại diện duy nhất gọi là vector **`[CLS]`** [12].

#### 2) Tinh chỉnh các Mô hình Mã nguồn (Fine-Tuning Code Models)
Như đã đề cập, chúng tôi tinh chỉnh CodeBERT và UniXcoder bằng hai kỹ thuật độc lập:

*   **Phương pháp FSL với Mạng Siamese (Siamese Network):**
    Mạng Siamese được huấn luyện với hàm mất mát bộ ba (**Triplet Loss Function** [45]) nhằm xác định độ tương đồng giữa các đầu vào bằng cách học một không gian nhúng [46]. Trong không gian này, các đầu vào tương tự nhau được đặt gần nhau hơn, trong khi các đầu vào khác biệt bị đẩy ra xa nhau. 
    Tương tự các công trình trước [23], chúng tôi xây dựng mạng Siamese gồm 3 mạng con giống hệt nhau (chia sẻ trọng số và tham số). Đầu vào của mạng là bộ ba: bài test neo (**Anchor**), bài test dương tính (**Positive** - cùng thể loại với Anchor), và bài test âm tính (**Negative** - khác thể loại với Anchor). Hàm Triplet Loss tối thiểu hóa khoảng cách giữa Anchor và Positive, đồng thời tối đa hóa khoảng cách giữa Anchor và Negative.
    
    Kiến trúc mỗi mạng con kế thừa từ Akli et al. [23]: gồm một lớp tuyến tính 512 nơ-ron, một lớp dropout ngẫu nhiên ngắt kết nối để chống quá khớp (overfitting) [49], và một lớp chuẩn hóa (normalization) trước khi tạo vector `[CLS]`. Mạng sử dụng bộ tối ưu hóa **AdamW** [50] với tốc độ học $10^{-5}$ và kích thước batch size bằng 2 (do giới hạn bộ nhớ GPU 8GB).
    
    Khi đánh giá mô hình FSL trên tập kiểm thử (query test): Một tập hỗ trợ (**Support Set**) gồm một số ít ví dụ của mỗi lớp (dương tính và âm tính) được trích từ tập huấn luyện. Ta tính vector trọng tâm (**centroid**) của từng lớp trong support set bằng trung bình cộng các vector `[CLS]`. Đối với ca kiểm thử query cần dự đoán, mô hình tính độ tương đồng cosine giữa vector của query với centroid của lớp dương tính và lớp âm tính; query sẽ được gán vào lớp có độ tương đồng cao nhất (**Hình 4**).

*   **Phương pháp Phân loại Nhị phân với FNN:**
    Vector `[CLS]` từ mô hình mã nguồn được đưa trực tiếp vào một mạng nơ-ron truyền thẳng (FNN) (**Hình 5**). Mạng FNN gồm: lớp đầu vào 768 nơ-ron, lớp ẩn 512 nơ-ron, và lớp đầu ra 2 nơ-ron. Mạng sử dụng hàm kích hoạt **ReLU** [51], lớp dropout [50], và hàm **Softmax** ở đầu ra để tính xác suất bài kiểm thử flaky có thuộc về thể loại bản vá đang xét hay không [12].

---

### C. Sửa chữa Bài kiểm thử Flaky bằng GPT và các Thể loại Bản vá Đề xuất (Repairing Flaky Tests Using GPT and Our Proposed Fix Categories)

Các Mô hình Ngôn ngữ Lớn (LLM) như GPT đã được áp dụng thành công trong nhiều tác vụ kỹ thuật phần mềm tự động [52], [53], bao gồm cả sửa lỗi chương trình tự động (Automated Program Repair - APR) [54], [55], [56], [57]. Vì vậy, chúng tôi muốn tìm hiểu:
- **(a)** Một mô hình GPT thương mại có sẵn có thể tự động sinh bản vá cho bài kiểm thử flaky hiệu quả đến mức nào;
- **(b)** Việc phân loại thể loại bản vá của chúng tôi có thể giúp GPT sửa chữa tính chập chờn tốt hơn như thế nào.

Chúng tôi sử dụng **GPT-3.5 Turbo** (175 tỷ tham số, cửa sổ ngữ cảnh 16.385 token, phiên bản phát hành ngày 06/11/2023). Theo công bố chính thức của OpenAI [58], mô hình này được huấn luyện trên dữ liệu tính đến tháng 9 năm 2021.

Mô hình GPT-4 (1,7 nghìn tỷ tham số) vượt trội hơn nhiều, tuy nhiên tập dữ liệu huấn luyện của nó kéo dài đến tháng 12 năm 2023 (hoặc tháng 4 năm 2023 ở phiên bản trước). Do phần lớn các bài test flaky trong tập dữ liệu của chúng tôi được đưa lên các kho chứa công khai trước các mốc thời gian này, việc sử dụng GPT-4 có thể dẫn đến **nguy cơ rò rỉ dữ liệu (data leakage)**. Do đó, chúng tôi chọn **GPT-3.5 Turbo** để đảm bảo tính khách quan và khoa học.

#### Cấu trúc Prompt GPT để Sửa chữa Flaky Tests:
Để đánh giá tác động của thể loại bản vá dự đoán, chúng tôi đưa thể loại dự đoán cùng mã nguồn bài test flaky vào prompt gửi cho GPT. Chúng tôi xây dựng 2 phương thức tạo prompt:
1.  **Prompt kèm Nhãn thể loại (With Label Prompt):** Cung cấp mã bài test flaky kèm nhãn thể loại bản vá tương ứng;
2.  **Prompt Học theo Ngữ cảnh (In-Context Learning Prompt):** Cung cấp mã bài test flaky cần sửa, nhãn thể loại dự đoán, cùng một vài ví dụ mẫu (few-shot demonstrations) gồm các bài test flaky trong cùng thể loại trích từ tập huấn luyện kèm bản vá của chúng. Nhờ đó, LLM học được chiến lược sửa lỗi đặc thù của thể loại đó ngay trong thời gian suy diễn [59] mà không cần tinh chỉnh mô hình tốn kém.


---

## III. ĐÁNH GIÁ THỰC NGHIỆM (VALIDATION)

Mục tiêu của nghiên cứu này là dự đoán thể loại bản vá cho một bài kiểm thử flaky nhằm hỗ trợ sinh ra phiên bản đã được sửa chữa hoàn chỉnh của bài kiểm thử đó. Phần này tiến hành đánh giá thực nghiệm phương pháp tiếp cận của chúng tôi (xem Mục II) bằng cách: đầu tiên giới thiệu các câu hỏi nghiên cứu và giải thích quy trình thu thập dữ liệu; tiếp theo thảo luận về thiết kế thực nghiệm và báo cáo các kết quả đạt được.

---

### A. Các Câu hỏi Nghiên cứu (Research Questions)

Trong nghiên cứu này, chúng tôi giải quyết ba câu hỏi nghiên cứu cốt lõi sau:

*   **RQ1: Quy trình tự động gán nhãn thể loại bản vá kiểm thử flaky được đề xuất đạt độ chính xác như thế nào?**  
    *Động lực:* Do hiện tại chưa có bộ dữ liệu kiểm thử flaky nào được gán nhãn sẵn theo thể loại bản vá, trong RQ này, chúng tôi kiểm chứng quy trình tự động gán nhãn một bài kiểm thử flaky dựa trên bản vá của nó. Nếu được tự động hóa một cách chính xác, quy trình này sẽ rất hữu ích vì nó có thể chuyển đổi bất kỳ bộ dữ liệu kiểm thử flaky nào (miễn là có chứa bản vá) thành một tập huấn luyện phù hợp để xây dựng các mô hình dự đoán (như các mô hình trong RQ2). Trong thực tế, một tập huấn luyện tùy biến (từ các dự án nội bộ của tổ chức) thường rất cần thiết để nắm bắt tri thức đặc thù miền, phục vụ việc huấn luyện mô hình mới từ đầu hoặc tinh chỉnh mô hình tiền huấn luyện, điều này càng củng cố thêm tính cấp thiết của một kỹ thuật gán nhãn tự động.

*   **RQ2: Hiệu quả của các mô hình ngôn ngữ khác nhau (CodeBERT và UniXcoder, khi có và không có FSL) trong việc dự đoán thể loại bản vá từ mã kiểm thử flaky đạt mức độ nào?**  
    *Động lực:* Hầu hết các mô hình dự đoán hiện có liên quan đến flaky test đều cố gắng dự đoán xem một bài test có flaky hay không. FlakyCat [23] là cách tiếp cận duy nhất phân loại bài kiểm thử flaky theo nguyên nhân gốc rễ (root cause) bằng CodeBERT và FSL. Tuy nhiên, việc chỉ xác định nguyên nhân gốc rễ không trực tiếp hỗ trợ kiểm thử viên giải quyết tính chập chờn. Ví dụ: một nguyên nhân gốc rễ được FlakyCat đề xuất là *Unordered Collections* (tập hợp không có thứ tự). Phân loại giải pháp của Parry et al. [20] ánh xạ nguyên nhân này vào thể loại bản vá *Guarantee Order* (đảm bảo thứ tự) nhưng không cung cấp chỉ dẫn cụ thể về cách làm thế nào để đảm bảo thứ tự đó. 
    Ngược lại, các thể loại bản vá do chúng tôi định nghĩa cung cấp ánh xạ một-đối-một giữa các bản vá cụ thể với từng ca kiểm thử. Ví dụ: đối với nguyên nhân *Unordered Collections*, Bảng II đưa ra nhiều thể loại bản vá cụ thể như *Reorder Data*, *Change Data Structure*, hoặc *Reorder Parameters*. Tùy thuộc vào mã kiểm thử, một trong các bản vá cụ thể này sẽ được dự đoán làm thể loại bản vá. Cách tiếp cận này mang lại cho kiểm thử viên các giải pháp chính xác hơn thay vì một nhãn chung chung như *Guarantee Order*. Sự khác biệt thực tiễn giữa bản vá và nguyên nhân gốc rễ đã thôi thúc chúng tôi khám phá các phương pháp thay thế để phân loại bài kiểm thử theo thể loại bản vá cần thiết. Trong RQ này, chúng tôi khảo sát hai mô hình mã nguồn đại diện cho SOTA và nghiên cứu tác động của FSL đối với từng mô hình.

*   **RQ3: Năng lực của GPT-3.5 Turbo trong việc sửa chữa một bài kiểm thử flaky cho trước đạt hiệu quả ra sao, khi có và không có thông tin về thể loại bản vá cũng như các ví dụ bản vá mẫu?**  
    *Động lực:* Khi đã có thể loại bản vá, câu hỏi tiếp theo là: việc có được thông tin đó sẽ giúp ích đến mức nào trong việc sửa chữa tính chập chờn? Để trả lời, chúng tôi tập trung vào phương pháp sửa chữa tự động hoàn toàn và đánh giá xem liệu việc biết thể loại kiểm thử flaky có giúp tạo ra bản vá tốt hơn hay không. Chúng tôi dựa vào các LLM được tiền huấn luyện trên kho ngữ liệu khổng lồ để sinh mã hoàn chỉnh mà không cần tinh chỉnh mô hình. RQ3 điều tra xem liệu các thể loại bản vá được dự đoán từ RQ2 có nâng cao hiệu năng của GPT trong việc sửa chữa bài kiểm thử flaky hay không và chúng tôi có thể đạt được các bản vá chính xác ở mức độ nào. Ngoài ra, chúng tôi sử dụng học theo ngữ cảnh (in-context learning) để xem năng lực sửa lỗi của GPT cải thiện ra sao khi được cung cấp các ví dụ về một kiểu bản vá cụ thể đi kèm nhãn thể loại được đề xuất.

---

### B. Bộ Dữ liệu và Tăng cường Dữ liệu (Dataset and Data Augmentation)

Để tạo ra một bộ dữ liệu có nhãn về các thể loại bản vá phục vụ nghiên cứu, trước tiên chúng tôi phân tích các tập dữ liệu kiểm thử flaky hiện có có chứa bản vá, sau đó chọn tập dữ liệu phù hợp nhất và tăng cường nó bằng các nhãn tự động sinh ra.

#### 1) Các Bộ Dữ liệu Hiện có (Existing Datasets)
Chưa có bộ dữ liệu công khai nào về kiểm thử flaky được gán nhãn dựa trên bản chất bản vá của chúng. Hầu hết các tập dữ liệu hiện có (như FlakeFlagger [14]) chỉ chứa các nhãn nhị phân biểu thị tính chập chờn. Tập dữ liệu trong FlakyCat [23] gán nhãn dựa trên nguyên nhân chứ không phải bản vá. Các nghiên cứu trước đây về sửa chữa flaky test dựa trên các tập dữ liệu rất hạn chế về quy mô:
- Tập **Flex** [62] chỉ bao gồm 35 bài test flaky;
- Eck và cộng sự [63] phân tích 200 bài test flaky từ cơ sở dữ liệu của Mozilla;
- Tập **ShowFlakes** [20] bao gồm 75 commit từ 31 dự án Python, nhưng chỉ có 20 bài test có thể sửa được bằng cách can thiệp vào mã kiểm thử;
- Tập **iPFlakies** và **iFixFlakies** [35], [64] có quy mô lớn hơn nhưng nguyên nhân chập chờn lại liên quan đến thứ tự thực thi kiểm thử (Order Dependency) chứ không phải logic mã kiểm thử.

Bộ dữ liệu lớn nhất và phù hợp nhất hiện có là **International Dataset of Flaky Tests (IDoFT)** [^13]. Chúng tôi thu thập tập dữ liệu Java từ IDoFT tính đến ngày 23/10/2023:
- Dữ liệu ban đầu gồm **5.500 bài kiểm thử** (chứa 128 bài trùng lặp). Sau khi khử trùng lặp, còn lại **5.372 bài kiểm thử**.
- Lọc các bài kiểm thử có bản vá đã được chấp nhận (PR được merge trên GitHub), thu được **788 bài kiểm thử**.
- Phân tích diff giữa bài test flaky và bản vá của lập trình viên, chúng tôi loại bỏ 226 bài test chỉ sửa trong mã sản phẩm (CUT) mà không sửa mã test.
- Kết quả thu được **562 bài kiểm thử flaky** được sửa bằng cách can thiệp vào mã kiểm thử, bắt nguồn từ **123 dự án Java khác nhau**. Đây là kho lưu trữ lớn nhất hiện có về các bài test flaky có thể sửa được qua mã kiểm thử.

[^13]: `https://mir.cs.illinois.edu/flakytests`

#### 2) Bộ Dữ liệu Có Nhãn về các Thể loại Bản vá (Labeled Dataset)
Áp dụng quy trình gán nhãn tự động ở Mục II, chúng tôi thu được bộ dữ liệu có nhãn (công khai trên Figshare [^14]). 

Do phân bố dữ liệu giữa các thể loại bị mất cân bằng và để đảm bảo mô hình có đủ mẫu tối thiểu để học, chúng tôi **chọn các thể loại có ít nhất 30 bài kiểm thử** để đưa vào tập huấn luyện. Kết quả là **9 thể loại bản vá hàng đầu** trong Bảng II được chọn. Vì một bài test có thể có nhiều nhãn, chúng tôi chuyển đổi bài toán thành **9 tập nhãn nhị phân riêng biệt**, mỗi tập tương ứng với một thể loại bản vá (lớp dương tính: thuộc thể loại đó; lớp âm tính: thuộc các thể loại khác).

[^14]: Gói replication package: `https://figshare.com/s/47f0fb6207ac3f9e2351`

#### 3) Tăng cường Dữ liệu cho Học Ít Mẫu (Data Augmentation for FSL)
- Đối với mô hình **không dùng FSL** (tinh chỉnh với FNN): Chúng tôi áp dụng kỹ thuật **Random Oversampling** [12], [65] bằng cách nhân bản ngẫu nhiên các mẫu thuộc lớp thiểu số trong tập huấn luyện để cân bằng dữ liệu.
- Đối với mô hình **dùng FSL với Mạng Siamese**: Chúng tôi áp dụng kỹ thuật tăng cường dữ liệu đột biến [66], [67] để tổng hợp thêm các bộ ba `<Anchor, Positive, Negative>` hợp lệ:
  - Nếu tập huấn luyện gốc có 20 mẫu, việc tăng cường sẽ tạo thêm 20 mẫu positive mới và 20 mẫu negative mới, nâng tổng số lên 60 mẫu.
  - Kỹ thuật đột biến mã nguồn kiểm thử: Thay đổi tên hàm test (ví dụ: `postFeedSerializationTest` thành `postFeedSerializationTest_xacu4`) và thay thế giá trị các biến ngẫu nhiên (ví dụ: biến số nguyên `access point` đổi từ `1` thành `8967`; biến chuỗi đổi từ `AMAZON-US-HQ` thành `AMAZON-"RZjqJ"-HQ`). Toàn bộ các câu lệnh gây chập chờn được giữ nguyên vẹn.

#### 4) Lựa chọn Dữ liệu để Đánh giá với Mô hình GPT (Data Selection for GPT Evaluation)
Để đánh giá GPT-3.5 Turbo trong RQ3 mà **không bị rò rỉ dữ liệu (data leakage)**, do GPT-3.5 được huấn luyện trên dữ liệu trước tháng 9 năm 2021, chúng tôi **chỉ chọn các bài kiểm thử được sửa hoặc thêm vào sau tháng 9/2021**. Tiêu chí loại trừ này mang lại **181 bài kiểm thử flaky từ 61 dự án riêng biệt**, bao gồm đại diện của tất cả 9 thể loại bản vá.

#### 5) Lựa chọn Dữ liệu để Thực thi Kiểm thử Sau khi Sửa (Data Selection for Execution)
Trong số 181 bài test từ 61 dự án trên, chúng tôi chọn các dự án có ít nhất 5 ca kiểm thử flaky, thu được 9 dự án. Trong 9 dự án này:
- 4 dự án không thể build/thực thi được trên máy cục bộ do thiếu phụ thuộc môi trường hoặc commit cũ bị xóa/merge;
- **5 dự án thực thi thành công hoàn toàn**, với tổng cộng **35 ca kiểm thử flaky**. Chi tiết 35 bài test này được cung cấp trong gói replication package để chạy đối chứng thực tế.

---

### C. Thiết kế Thực nghiệm (Experimental Design)

#### 1) Các Đường cơ sở So sánh (Baselines)
Đây là nghiên cứu đầu tiên tự động phân loại thể loại bản vá và sinh bản vá hoàn chỉnh cho flaky test chỉ dựa vào mã kiểm thử. Do đó:
- Không thể so sánh với các bộ phân loại ML truyền thống vì chúng đòi hỏi các đặc trưng động phức tạp (lịch sử thực thi, coverage trên production code);
- Không dùng RNN hay LSTM cơ bản vì chúng không được tiền huấn luyện trên code, đòi hỏi tập dữ liệu khổng lồ để tránh overfitting [68], [69];
- Chúng tôi so sánh đối chứng giữa hai mô hình mã nguồn SOTA là **CodeBERT** và **UniXcoder**, mỗi mô hình được khảo sát ở 2 biến thể: **có FSL** (Mạng Siamese) và **không có FSL** (mạng FNN).

#### 2) Huấn luyện và Đánh giá Mô hình Dự đoán (Training & Testing Protocol)
Chúng tôi sử dụng quy trình **Kiểm định chéo 4 đoạn phân tầng (Stratified 4-fold cross-validation)** để đảm bảo phân chia train-test không thiên vị. Trong đó: 3 phần dùng để huấn luyện và 1 phần dùng để kiểm thử. Trong tập huấn luyện, 30% dữ liệu được tách riêng làm tập validation để kiểm soát overfitting/underfitting. Chúng tôi chủ ý không dùng 10-fold vì các thể loại nhỏ (như *Change Data Format* chỉ có 33 mẫu dương tính) sẽ không còn đủ mẫu dương tính trong mỗi fold.

#### 3) Thiết kế Prompt cho GPT (Prompt Design)
Chúng tôi thiết kế 3 dạng prompt:
1.  **Prompt Không nhãn (No Label Prompt - Hình 6):** Chỉ truyền mã kiểm thử flaky và yêu cầu GPT sinh bản vá;
2.  **Prompt Kèm nhãn (Label Prompt - Hình 7):** Truyền mã kiểm thử flaky kèm theo nhãn thể loại bản vá được dự đoán từ mô hình mã nguồn;
3.  **Prompt Học theo ngữ cảnh (In-Context Learning Prompt - Hình 8):** Mở rộng từ dạng 2 bằng cách cung cấp thêm 5 ví dụ mẫu bài test kèm bản vá trong cùng thể loại trích từ tập huấn luyện. Kỹ thuật này được thử nghiệm trên 3 thể loại lớn nhất (> 30 mẫu trong tập 181 test): *Change Assertion* (64 mẫu), *Change Data Structure* (41 mẫu), và *Change Condition* (41 mẫu) — tổng cộng 146 bài test. Trừ đi 15 mẫu làm ví dụ (5 mẫu × 3 thể loại), còn lại **131 bài kiểm thử** được đánh giá trong thí nghiệm in-context learning.
Prompt yêu cầu rõ ràng: **chỉ trả về mã kiểm thử đã sửa**, không kèm văn bản giải thích tự nhiên, giúp mã có thể đưa thẳng vào kiểm thử mà không cần hậu xử lý.

#### 4) Thực thi Ca Kiểm thử (Test Case Execution Protocol)
Với 35 bài test có thể thực thi từ 5 dự án:
- Đầu tiên, chạy phiên bản sửa gốc của nhà phát triển **10 lần liên tiếp** để xác nhận bản vá thực sự ổn định;
- Tiếp theo, chạy phiên bản do LLM sinh ra **10 lần liên tiếp**. Một bài test được coi là pass nếu nó pass nhất quán trong toàn bộ 10 lần chạy; nếu fail ở bất kỳ lần nào, nó được ghi nhận là fail.

#### 5) Các Độ đo Đánh giá (Evaluation Metrics)
- **Đánh giá mô hình phân loại:** Sử dụng **Precision**, **Recall**, và **F1-Score**. Chúng tôi đặc biệt nhấn mạnh **Precision**: Khi hệ thống báo bài test thuộc thể loại *Change Assertion*, kiểm thử viên cần có sự tự tin cao độ để tập trung sửa vào câu lệnh assert mà không bị dẫn dắt sai hướng gây lãng phí tài nguyên [70], [71].
- **Kiểm định Thống kê Phân loại:** Dùng **Kiểm định Fisher chính xác (Fisher's Exact Test)** [72] để đánh giá sự khác biệt hiệu năng giữa 4 phương pháp phân loại; dùng hệ số **Cohen's Kappa** [36] để đo độ đồng thuận gán nhãn ban đầu.
- **Đánh giá Chất lượng Sinh Mã:** Sử dụng họ độ đo BLEU: **Corpus BLEU**, **Sentence BLEU**, và đặc biệt là **CodeBLEU** [77] — độ đo kết hợp toàn diện cả cú pháp và ngữ nghĩa của mã nguồn theo công thức:

$$\text{CodeBLEU} = \alpha \cdot \text{BLEU} + \beta \cdot \text{BLEU}_{\text{weight}} + \gamma \cdot \text{Match}_{\text{ast}} + \delta \cdot \text{Match}_{\text{df}} \quad (1)$$

Trong đó:
- $\text{BLEU}$: Đo độ trùng lặp $n$-gram tiêu chuẩn giữa mã sinh ra và mã tham chiếu;
- $\text{BLEU}_{\text{weight}}$: Khớp $n$-gram có trọng số, gán trọng số cao hơn cho các từ khóa quan trọng (`int`, `public`, `char`...);
- $\text{Match}_{\text{ast}}$: Khớp cây cú pháp trừu tượng (AST), đánh giá cấu trúc ngữ pháp;
- $\text{Match}_{\text{df}}$: Khớp luồng dữ liệu (Data-flow match), phân tích đồ thị tương tác và dòng chảy của các biến;
- Các trọng số $\alpha = \beta = \gamma = \delta = 0,25$ (theo chuẩn của Ren et al. [77]).

- **Ước tính Tỷ lệ Pass trên Diện rộng:** Dùng **Bootstrapping** [78] (độ tin cậy 95%) từ mẫu 35 bài test thực thi để ước tính cận trên và cận dưới tỷ lệ pass cho toàn bộ tập dữ liệu. Đồng thời, xây dựng mô hình **Hồi quy Logistic (Logistic Regression)** [79] dựa trên điểm CodeBLEU để dự đoán xác suất pass của các bài test không thể thực thi.
- **Xác minh Tính tương đương Ngữ vi (Behavioral Equivalence):** Với các bài test pass có CodeBLEU < 100%, chúng tôi kiểm tra thủ công để đảm bảo bản vá không làm suy yếu năng lực bắt lỗi của bộ kiểm thử.
- **Đo lường Mức độ Sửa đổi (Cho các bài test fail):** Tính khoảng cách hiệu chỉnh **Levenshtein Edit Distance** [80] để đo tỷ lệ phần trăm token cần sửa đổi thêm để đạt tới bản vá chuẩn của lập trình viên.
- **Kiểm định Ý nghĩa Thống kê Sửa lỗi:** Sử dụng kiểm định phi tham số **Wilcoxon signed-rank test** [81] để so sánh sự khác biệt điểm CodeBLEU giữa các loại prompt.


---

### D. Kết quả Nghiên cứu (Results)

#### 1) Kết quả RQ1: Độ chính xác của Công cụ Gán nhãn Tự động
Để bắt đầu, 100 ca kiểm thử đã được chọn ngẫu nhiên và được gán nhãn độc lập bởi hai nhà nghiên cứu (thuộc nhóm đồng tác giả của công trình này). Điểm hệ số Kappa Cohen đạt được là 0,65, cho thấy mức độ đồng thuận vừa phải (moderate agreement) giữa hai người đánh giá. Các bất đồng giữa họ cuối cùng đã được giải quyết thông qua nhiều vòng thảo luận để thống nhất các thể loại bản vá được sử dụng bởi công cụ gán nhãn tự động.

Để đánh giá độ chính xác gán nhãn của công cụ tự động, chúng tôi lấy một tập ngẫu nhiên khác gồm 200 bài kiểm thử flaky và thu nhận các nhãn thể loại bản vá từ công cụ. Sau đó, chính hai nhà nghiên cứu này đã gán nhãn thủ công cho các bài kiểm thử đó, cho phép tính toán độ chính xác của công cụ gán nhãn tự động như được thể hiện trong **Hình 2**. Chúng tôi nhận thấy công cụ đạt độ chính xác lên tới **98,5%**, chỉ có ba bài kiểm thử bị gán nhãn nhầm với nhiều thể loại bản vá khác nhau (bao gồm cả thể loại đúng).

> **Tóm tắt RQ1:** Hệ thống gán nhãn tự động đề xuất cho các bài kiểm thử flaky đã được đánh giá và đạt độ chính xác 98,5% trong việc gán nhãn chính xác một tập gồm 200 bài kiểm thử với các thể loại bản vá khác nhau. Việc sở hữu một công cụ gán nhãn tự động và chuẩn xác là yếu tố thiết yếu cho nghiên cứu này, cho các công trình tương lai, và trong thực tiễn kỹ nghệ khi xây dựng các mô hình dự đoán trong ngữ cảnh dự án.

---

#### 2) Kết quả RQ2: Dự đoán Thể loại Bản vá Kiểm thử Flaky
**Bảng III** trình bày kết quả dự đoán cho toàn bộ chín thể loại bản vá kiểm thử flaky sử dụng bốn phương pháp tiếp cận khác nhau: CodeBERT và UniXcoder, được tinh chỉnh cùng với Mạng Siamese hoặc Mạng FNN truyền thống. Trong trường hợp Mạng Siamese, chúng tôi đánh giá cả hai mô hình ngôn ngữ khi có áp dụng Học ít mẫu (Few-Shot Learning - FSL).

##### BẢNG III: So sánh kết quả dự đoán cho từng thể loại bản vá sử dụng CodeBERT (CB) và UniXcoder (UC), cả khi có và không có FSL. (Giá trị cao nhất của mỗi độ đo cho từng thể loại được in đậm)

| Thể loại | Precision (%) CB | Precision (%) CB w/ FSL | Precision (%) UC | Precision (%) UC w/ FSL | Recall (%) CB | Recall (%) CB w/ FSL | Recall (%) UC | Recall (%) UC w/ FSL | F1 (%) CB | F1 (%) CB w/ FSL | F1 (%) UC | F1 (%) UC w/ FSL |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CA** | 88 | 86 | **96** | 93 | **88** | 86 | 86 | 85 | 88 | 86 | **91** | 89 |
| **CDS** | 86 | 76 | **89** | 85 | 86 | 71 | **87** | 81 | 87 | 74 | **88** | 83 |
| **HE** | 97 | 95 | **98** | 95 | 87 | 88 | 89 | **90** | 92 | 91 | **93** | **93** |
| **RV** | 88 | 91 | 94 | **96** | **98** | 95 | 97 | 96 | 93 | 93 | **96** | **96** |
| **CC** | **91** | 84 | 87 | 74 | 84 | 70 | **87** | 70 | **87** | 76 | **87** | 72 |
| **RD** | 88 | 80 | **96** | 90 | 82 | **88** | 72 | **88** | 85 | 84 | 82 | **89** |
| **CDF** | 96 | **97** | 90 | 90 | 93 | **97** | 94 | 90 | 96 | **97** | 93 | 95 |
| **MC** | **83** | 79 | 82 | 76 | **67** | 61 | 62 | 61 | **74** | 70 | 70 | 68 |
| **RP** | 53 | 48 | **91** | 88 | **94** | 88 | 91 | 82 | 64 | 68 | **91** | 85 |

*(Chú thích viết tắt: CA: Change Assertion; CDS: Change Data Structure; HE: Handle Exception; RV: Reset Variable; CC: Change Condition; RD: Reorder Data; CDF: Change Data Format; MC: Miscellaneous; RP: Reorder Parameters).*

UniXcoder không dùng FSL thể hiện độ chính xác Precision vượt trội và Recall tương đương trong các thể loại *Change Assertion*, *Change Data Structure*, *Handle Exception*, *Change Condition*, và *Reorder Parameters*, với Precision lần lượt là **96%**, **89%**, **98%**, **87%**, và **91%**, vượt qua cả ba phương pháp còn lại. Đối với *Reorder Data*, một lần nữa UniXcoder không FSL đạt điểm Precision cao nhất là **96%**. Tuy nhiên, khi tích hợp FSL, UniXcoder thể hiện Recall vượt trội hơn là **88%**. Hơn nữa, CodeBERT không FSL cho kết quả nhỉnh hơn một chút ở thể loại *Miscellaneous*, với 83% Precision và 67% Recall, mặc dù sự khác biệt so với UniXcoder là không có ý nghĩa thống kê.

Đối với thể loại *Reset Variable*, UniXcoder kèm FSL mang lại độ chính xác rất cao với 96% Precision và 97% Recall, trong khi CodeBERT không FSL đạt Recall nhỉnh hơn là 98% nhưng với Precision thấp hơn (88%). Cuối cùng, đối với *Change Data Format*, CodeBERT kèm FSL vượt qua tất cả các cách tiếp cận khác với 97% ở cả Precision và Recall. Tuy nhiên, sự khác biệt so với UniXcoder một lần nữa không có ý nghĩa thống kê.

Các thể loại *Change Data Format*, *Handle Exception*, *Reset Variable*, *Reorder Data*, và *Change Assertion* là những thể loại dễ phân loại nhất đối với cả bốn phương pháp, với điểm Precision trung bình (tính trên cả 4 cách tiếp cận) lần lượt là **93%**, **96%**, **92%**, **88%**, và **90%**. Điều này nhiều khả năng là do tần suất xuất hiện cao của các từ khóa đặc trưng trong mã kiểm thử dành cho xử lý ngoại lệ, câu lệnh assert, reset biến, và sắp xếp lại dữ liệu (với các từ khóa như `sort` và `order by`). Trong trường hợp thể loại *Change Data Format*, mô hình tìm kiếm một chuỗi dài phức tạp được truyền vào một hàm. Những chuỗi này dễ nhận diện hơn vì chúng tôi quan sát thấy tất cả các bài kiểm thử flaky thuộc thể loại này đều chứa một chuỗi dài phức tạp cần được cập nhật để loại bỏ tính flaky. 

Cả bốn mô hình đều thể hiện hiệu năng mạnh mẽ trên hầu hết các thể loại bản vá, cho thấy Recall và Precision cao. Tuy nhiên, ở thể loại *Miscellaneous*, hiệu năng giảm đi đáng kể, chỉ đạt trung bình 62% Recall. Hiệu năng thấp này có thể là do sự vắng mặt của các mẫu code chung hoặc các từ khóa cụ thể xuyên suốt các bài test trong thể loại này, vốn không thể kỳ vọng là đồng nhất. Hơn nữa, ở thể loại *Reorder Parameters*, CodeBERT (cả khi có và không có FSL) thể hiện Precision thấp hơn đáng kể so với UniXcoder (53% và 48% so với 91% và 88%). Chi tiết sâu hơn về các trường hợp phân loại sai của các mô hình được phân tích trong Mục IV.

Nhìn chung, các kết quả trong Bảng III chỉ ra rằng đối với hầu hết các thể loại bản vá, UniXcoder vượt trội hơn CodeBERT một cách có ý nghĩa thống kê, dựa trên Kiểm định Fisher chính xác (Fisher's Exact Test) với mức ý nghĩa $\alpha = 0,05$. Tuy nhiên, việc áp dụng FSL không cải thiện đáng kể hiệu năng của UniXcoder, điều này có thể xuất phát từ việc tập dữ liệu bị giới hạn với chỉ một số lượng nhỏ các cá thể dương tính ở hầu hết các thể loại bản vá, gây cản trở cho quá trình tinh chỉnh mô hình.

> **Tóm tắt RQ2:** UniXcoder vượt trội hơn CodeBERT trong việc dự đoán hầu hết các thể loại bản vá, với Precision và Recall cao hơn. Việc sử dụng kỹ thuật Học ít mẫu (FSL) không cải thiện đáng kể độ chính xác dự đoán của UniXcoder.

---

#### 3) Kết quả RQ3: Sửa chữa Mã Kiểm thử Flaky Tự động bằng LLM
**Bảng IV** báo cáo kết quả đánh giá được sinh bởi mô hình GPT-3.5 Turbo khi tiếp nhận mã kiểm thử flaky đầu vào và tạo ra phiên bản đã sửa lỗi, so sánh giữa trường hợp có và không có nhãn thể loại bản vá dự đoán của chúng tôi. Các độ đo đánh giá bao gồm điểm trung vị (Median) và trung bình (Mean) cho Corpus BLEU, Sentence BLEU, và CodeBLEU trên toàn bộ 181 bài kiểm thử flaky trong tập test.

##### BẢNG IV: Đánh giá mã kiểm thử flaky do GPT-3.5 sinh ra bằng điểm BLEU trên tất cả các thể loại cho 181 bài test flaky

| Độ đo (Metrics) | Prompt Kèm Nhãn (Mean) | Prompt Kèm Nhãn (Median) | Prompt Không Nhãn (Mean) | Prompt Không Nhãn (Median) |
| :--- | :---: | :---: | :---: | :---: |
| **Corpus BLEU** | 76 | 82 | 69 | 75 |
| **Sentence BLEU** | 77 | 82 | 70 | 76 |
| **CodeBLEU** | 81 | 85 | 75 | 81 |

Việc bổ sung nhãn thể loại bản vá dự đoán vào prompt đã làm tăng điểm trung vị của cả ba độ đo thêm lần lượt **7%**, **6%**, và **4%** đối với Corpus BLEU, Sentence BLEU, và CodeBLEU. Những cải thiện này đều có ý nghĩa thống kê dựa trên kiểm định phi tham số Wilcoxon signed-rank ở mức ý nghĩa $\alpha = 0,05$, với giá trị $p < 0,0001$ trong cả ba trường hợp.

Sự cải thiện này bắt nguồn từ thông tin bổ sung được cung cấp cho mô hình GPT, giúp mô hình định vị chính xác và giải quyết trực diện các vấn đề gây ra tính flaky của bài kiểm thử. Phát hiện này cũng gián tiếp chỉ ra rằng các thể loại bản vá được chúng tôi định nghĩa là rất rõ ràng, chuẩn xác và có thể hỗ trợ hiệu quả cho các kiểm thử viên trong việc xác định các phân đoạn mã cụ thể cần chỉnh sửa. Trong phần còn lại của RQ này, chúng tôi tập trung báo cáo điểm **CodeBLEU**, vì đây là độ đo được thiết kế chuyên biệt để đánh giá trực tiếp ngữ nghĩa và cú pháp của mã nguồn thay vì văn bản ngôn ngữ tự nhiên, mang lại sự đánh giá chính xác hơn cho mã kiểm thử được sinh ra.

**Bảng V** thể hiện điểm CodeBLEU trung vị và trung bình cho từng thể loại bản vá, khi có và không có thông tin nhãn.

##### BẢNG V: Điểm CodeBLEU trung bình và trung vị theo từng thể loại bản vá, khi có và không có nhãn thể loại bản vá trong prompt GPT

| Thể loại Bản vá (Fix Categories) | Có Nhãn (Mean) | Có Nhãn (Median) | Không Nhãn (Mean) | Không Nhãn (Median) | Số lượng mẫu (Count) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Change Assertion** | 80 | 85 | 76 | 79 | 64 |
| **Change Condition** | 87 | 90 | 84 | 89 | 41 |
| **Change Data Structure** | 87 | 81 | 72 | 82 | 41 |
| **Miscellaneous (Misc)** | 76 | 83 | 75 | 82 | 22 |
| **Change Data Format** | 77 | 80 | 60 | 58 | 13 |
| **Reorder Parameters** | 86 | 86 | 77 | 83 | 10 |
| **Reorder Data** | 71 | 73 | 69 | 73 | 5 |
| **Handle Exceptions** | 66 | 73 | 59 | 60 | 7 |
| **Reset Variable** | 95 | 95 | 95 | 95 | 1 |

Như có thể thấy, ở hầu hết các thể loại, việc cung cấp nhãn đều giúp cải thiện cả điểm trung bình lẫn trung vị CodeBLEU. Mức độ cải thiện theo từng thể loại dao động từ 0% đến 17% đối với điểm trung bình và từ -1% đến 22% đối với điểm trung vị CodeBLEU. Các mức cải thiện nhỏ hơn thường rơi vào những thể loại có rất ít mẫu (ví dụ: *Reset Variable* chỉ có 1 mẫu duy nhất) hoặc khi kết quả vốn dĩ đã rất cao (ví dụ: *Change Condition* đã đạt điểm trung vị CodeBLEU 89% ngay cả khi không có nhãn). Thể loại duy nhất có điểm trung vị giảm nhẹ (1%) sau khi cung cấp nhãn là thể loại *Miscellaneous*. Điều này rất có thể là do nhãn "Misc" (Hỗn hợp) không mang lại thông tin chỉ dẫn thực tế nào về cách khắc phục lỗi flaky.

Để mở rộng phân tích sang phương pháp prompt thứ ba (**Học theo ngữ cảnh - In-Context Learning**), **Bảng VI** so sánh cả ba phương pháp tiếp cận đối với ba thể loại bản vá lớn nhất: *Change Assertion*, *Change Data Structure*, và *Change Condition*. Như đã giải thích, chúng tôi chỉ tập trung vào ba thể loại này vì sau khi trích 5 mẫu mỗi thể loại làm ví dụ minh họa trong context, chỉ có ba thể loại này là còn đủ số lượng mẫu để tiến hành phân tích thỏa đáng và chạy các kiểm định thống kê.

##### BẢNG VI: So sánh điểm CodeBLEU trung bình và trung vị cho các thể loại bản vá khác nhau khi sử dụng nhãn thể loại bản vá và Học theo ngữ cảnh (In-Context Learning)

| Thể loại Bản vá | Không Nhãn (Mean) | Không Nhãn (Median) | Có Nhãn (Mean) | Có Nhãn (Median) | In-Context Learning (Mean) | In-Context Learning (Median) | Số lượng mẫu (Count) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Change Assertion** | 77 | 80 | 79 | 84 | 79 | 85 | 59 |
| **Change Data Structure** | 75 | 81 | 80 | 87 | **86** | **94** | 36 |
| **Change Condition** | 85 | 88 | 88 | 90 | **92** | **97** | 36 |

Nhìn vào bảng trên, chúng ta thấy rằng đối với thể loại *Change Data Structure*, điểm CodeBLEU trung bình và trung vị tăng tương ứng từ 80% lên **86%** và từ 87% lên **94%** khi áp dụng in-context learning so với việc chỉ đơn thuần cung cấp nhãn. Tương tự, đối với thể loại *Change Condition*, điểm trung bình và trung vị tăng tương ứng từ 88% lên **92%** và từ 90% lên **97%**. Tuy nhiên, trong trường hợp thể loại *Change Assertion*, không có sự cải thiện rõ rệt nào trong hiệu năng của mô hình sau khi được cung cấp một số lượng hạn chế các ví dụ minh họa. Nguyên nhân có thể do tính biến thiên rất lớn của các câu lệnh assertion trong mã kiểm thử, gợi ý rằng có thể tồn tại nhiều cách tiếp cận khác nhau để sửa câu lệnh assert nhằm giải quyết lỗi flaky. Rất có thể số lượng và sự đa dạng của các ví dụ minh họa được đưa vào là chưa đủ để mô hình nắm bắt được toàn bộ phổ phong phú của các bản vá liên quan đến assertion.

Hơn nữa, như được thể hiện qua biểu đồ hộp (boxplots) ở **Hình 11**, phân phối tổng thể của điểm CodeBLEU cho thấy phương sai đáng kể đối với tất cả các loại prompt và ba thể loại bản vá. Giá trị nhỏ nhất (minimum) ở mức thấp trong tất cả các trường hợp cho thấy vẫn tồn tại những bài kiểm thử flaky không thể sửa được bất kể sử dụng chiến lược prompt nào. Tuy nhiên, khi quan sát CodeBLEU trên cả ba thể loại đối với in-context learning, rõ ràng trong phần lớn các trường hợp, điểm CodeBLEU đều ở mức rất cao. Chẳng hạn, ngay cả đối với thể loại *Change Assertion* (thể loại có điểm tối thiểu thấp nhất), 75% số mẫu vẫn có CodeBLEU cao hơn 55%, và một nửa số ca kiểm thử có điểm CodeBLEU vượt trên 85%.

Do độ biến thiên trong các giá trị CodeBLEU theo từng thể loại, chúng tôi lại tiếp tục sử dụng kiểm định phi tham số Wilcoxon signed-rank với mức ý nghĩa $\alpha = 0,05$ để đảm bảo rằng những cải thiện quan sát được ở điểm trung vị là có ý nghĩa thống kê. Kết quả cho thấy khi xét tổng thể cả ba thể loại, so với cả prompt có nhãn và không nhãn, in-context learning tạo ra sự khác biệt có ý nghĩa thống kê vượt trội với $p < 0,001$. Tuy nhiên, khi xét riêng từng thể loại, sự khác biệt này so với prompt có nhãn chỉ có ý nghĩa thống kê đối với *Change Data Structure* ($p < 0,001$) và *Change Condition* ($p = 0,007$).

Trong các nghiên cứu tương lai, chúng tôi dự định khám phá một cách hệ thống việc sử dụng các prompt khác nhau bằng cách gia tăng số lượng và các dạng ví dụ minh họa, hoặc thử nghiệm các chiến lược kỹ nghệ prompt khác [75].

---

#### 4) Đánh giá Thông qua Thực thi Mã Kiểm thử Thực tế
Để có cái nhìn sâu sắc hơn về hiệu quả thực tế của các bản vá kiểm thử flaky do GPT sinh ra, chúng tôi đã tiến hành một loạt các đánh giá dựa trên kết quả thực thi kiểm thử. Vì những lý do đã nêu trong Mục III-B5, chúng tôi chỉ có thể thực thi tổng cộng **35 bài kiểm thử**, mỗi bài được chạy lặp lại **10 lần liên tiếp**, mang lại kết quả: **24 bài kiểm thử pass** và **11 bài kiểm thử fail**, với kết quả hoàn toàn nhất quán xuyên suốt 10 lần chạy lặp lại.

Từ 35 bài kiểm thử có thể thực thi được này (được sinh ra bằng prompt có kèm nhãn và ví dụ in-context đối với 3 thể loại khả dụng), trước tiên chúng tôi muốn ước tính tỷ lệ pass của các bài kiểm thử đã sửa trong khi vẫn tính đến độ bất định liên quan đến kích thước mẫu hạn chế này. Sử dụng kỹ thuật lấy mẫu lại **Bootstrapping** [78], chúng tôi ước tính khoảng tin cậy 95% cho tỷ lệ phần trăm các bài test pass nằm trong khoảng từ **51% đến 83%**. Khoảng ước lượng này mang tính thông tin rất hữu ích cho các kiểm thử viên trong thực tế—những người không có sẵn điểm CodeBLEU để đối chiếu và muốn biết trước mức độ kỳ vọng từ FlakyFix. Dựa trên kết quả này, chúng tôi kết luận rằng FlakyFix cung cấp một giải pháp sửa lỗi hiệu quả trong một tỷ lệ lớn các trường hợp.

Tiếp theo, chúng tôi kiểm tra mối quan hệ giữa kết quả thực thi (pass/fail) và điểm CodeBLEU tương ứng để xác định độ tin cậy của chỉ số CodeBLEU trong việc đánh giá mã test được sinh ra. Cụ thể, chúng tôi kỳ vọng rằng các bài test có điểm CodeBLEU cao hơn sẽ có xác suất pass cao hơn và ngược lại. Nhìn chung, điểm CodeBLEU trung bình giữa nhóm bài test pass và nhóm bài test fail lần lượt là **94%** và **74%**, củng cố nhận định rằng điểm CodeBLEU cao là một chỉ dấu mạnh mẽ cho việc bài test sẽ pass. Đặc biệt:
- Trong số 24 bài test pass, có tới **16 bài đạt điểm CodeBLEU tuyệt đối 100%**, biểu thị sự trùng khớp chính xác hoàn toàn với phiên bản sửa lỗi của lập trình viên ban đầu;
- Thêm vào đó, 22 bài test có điểm CodeBLEU lớn hơn hoặc bằng 80%;
- Ngược lại, trong số 11 bài test fail, chỉ có đúng 5 bài đạt điểm CodeBLEU $\ge 80\%$. 
- Đáng chú ý, có một bài test pass nhưng lại có điểm CodeBLEU thấp bất thường là **36%** (được minh họa trong **Hình 12**). Trường hợp này thể hiện một bản vá khác biệt về mặt cấu trúc code nhưng lại hoàn toàn đúng đắn về mặt ngữ vi thực thi. Trường hợp ngoại lệ này minh họa hoàn hảo cho giới hạn cố hữu của việc chỉ dựa vào các độ đo so khớp bề mặt mã nguồn như CodeBLEU.

##### Mô hình Hồi quy Logistic (Logistic Regression Model)
Để mô hình hóa một cách định lượng mối quan hệ giữa điểm CodeBLEU và xác suất pass của bài kiểm thử, chúng tôi huấn luyện một mô hình **Hồi quy Logistic (Logistic Regression - LR)** [79] trên 35 bài kiểm thử có thể thực thi, sử dụng nhãn pass/fail thực tế của chúng. Mô hình đạt độ chính xác **80%** trong việc dự đoán kết quả thực thi. Việc lựa chọn hồi quy logistic xuất phát từ kích thước mẫu nhỏ và thực tế là chúng tôi có một biến giải thích duy nhất (CodeBLEU) được kỳ vọng có mối quan hệ đơn điệu với xác suất bài test pass.

Mức độ phù hợp của mô hình (Goodness of fit) được đo lường bằng kiểm định Chi-Square [82], cho giá trị $p = 0,010$, khẳng định mối quan hệ có ý nghĩa thống kê giữa điểm CodeBLEU và xác suất bài test pass, bất chấp kích thước mẫu nhỏ. Đường cong hồi quy logistic thể hiện mối quan hệ giữa điểm CodeBLEU và xác suất pass được minh họa trong **Hình 9**, cho thấy xác suất pass tăng vọt rất mạnh khi điểm CodeBLEU vượt qua ngưỡng 50%.

```
+---------------------------------------------------------------------------------------------------+
| Hình 9: Đường cong Hồi quy Logistic thể hiện mối quan hệ giữa điểm CodeBLEU và xác suất test pass |
|                                                                                                   |
|  Xác suất Pass (Probability)                                                                      |
|   1.0 |                                                     * * * * *                             |
|   0.8 |                                                 * *                                       |
|   0.6 |                                             * *                                           |
|   0.4 |                                         * *                                               |
|   0.2 |                                   * * *                                                   |
|   0.0 | * * * * * * * * * * * * * * * * *                                                         |
|       +-----------------------------------------------------------------                          |
|         0          20         40         50        60        80       100   Điểm CodeBLEU         |
+---------------------------------------------------------------------------------------------------+
```

##### Ước tính Tỷ lệ Pass trên Toàn bộ Tập Dữ liệu Không Thể Thực thi
Để ước tính tỷ lệ bài test pass trong số các bài kiểm thử không thể thực thi được do thiếu môi trường phụ thuộc, chúng tôi áp dụng mô hình LR đã huấn luyện này để dự đoán kết quả cho chúng. Chúng tôi tính toán khoảng tin cậy 95% cho các xác suất dự đoán bằng cách sử dụng các sai số chuẩn thu được thông qua **phương pháp delta (delta method)** [83]. Phương pháp này cho phép xấp xỉ phương sai của xác suất dự đoán bằng cách trước tiên tính toán sai số chuẩn trên thang đo logit rồi chuyển đổi ngược lại sang thang đo xác suất. Nhờ đó, khoảng tin cậy tính đến mối quan hệ phi tuyến tính giữa logit và xác suất dự đoán, cung cấp thước đo độ bất định đáng tin cậy.

Theo các ước tính của chúng tôi:
- **Trên tập 181 bài test flaky:**
  - *Với prompt Không nhãn:* Khoảng tin cậy: 0,44 – 0,50 $\rightarrow$ Dự phóng có từ **80 (44%)** đến **91 (50%)** bài test sẽ pass.
  - *Với prompt Có nhãn:* Khoảng tin cậy: 0,51 – 0,57 $\rightarrow$ Dự phóng có từ **92 (51%)** đến **103 (57%)** bài test sẽ pass.
- **Trên tập 131 bài test flaky (tập áp dụng được In-Context Learning):**
  - *Với prompt Không nhãn:* Khoảng tin cậy: 0,44 – 0,52 $\rightarrow$ Dự phóng có từ **58 (44%)** đến **68 (52%)** bài test sẽ pass.
  - *Với prompt Có nhãn:* Khoảng tin cậy: 0,50 – 0,58 $\rightarrow$ Dự phóng có từ **66 (50%)** đến **76 (58%)** bài test sẽ pass.
  - *Với prompt In-Context Learning:* Khoảng tin cậy: 0,53 – 0,60 $\rightarrow$ Dự phóng có từ **69 (53%)** đến **79 (60%)** bài test sẽ pass.

**Bảng VII** và **Bảng VIII** tóm tắt các ước tính bài test pass dưới dạng cận dưới (Lower Bound) và cận trên (Upper Bound) qua các thiết lập prompt khác nhau cho tập 181 bài test và tập 131 bài test.

##### BẢNG VII: Ước tính số lượng bài test pass từ tập dữ liệu 181 test đối với các bản vá do GPT tạo ra khi có và không có nhãn thể loại bản vá trong prompt GPT

| Dạng Prompt | Cận dưới: Số bài pass | Cận dưới: Tỷ lệ pass (%) | Cận trên: Số bài pass | Cận trên: Tỷ lệ pass (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Prompt Không nhãn (With No Label)** | 80 | 44% | 91 | 50% |
| **Prompt Kèm nhãn (With Label)** | 92 | 51% | 103 | 57% |

##### BẢNG VIII: Ước tính số lượng bài test pass đối với các bản vá do GPT tạo ra sử dụng nhãn thể loại và Học theo ngữ cảnh (In-Context Learning) (áp dụng cho tập 131 bài test)

| Dạng Prompt | Cận dưới: Số bài pass | Cận dưới: Tỷ lệ pass (%) | Cận trên: Số bài pass | Cận trên: Tỷ lệ pass (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Prompt Không nhãn (With No Label)** | 58 | 44% | 68 | 52% |
| **Prompt Kèm nhãn (With Label)** | 66 | 50% | 76 | 58% |
| **Học theo ngữ cảnh (In-Context Learning)** | 69 | 53% | 79 | 60% |

Từ các kết quả trên, chúng tôi có thể kết luận rằng việc cung cấp nhãn thể loại bản vá trong prompt cho GPT thực sự tạo ra sự khác biệt rõ rệt về tỷ lệ bài kiểm thử pass. Nhìn chung, một tỷ lệ hợp lý các bài kiểm thử được sinh ra có kèm nhãn được dự đoán sẽ pass, dao động xấp xỉ từ **50% đến 60%** khi tính đến độ bất định thống kê.

---

#### 5) Phân tích Nỗ lực Sửa đổi Thủ công Đối với các Ca Kiểm thử Fail
Đối với **11 bài kiểm thử do GPT sinh ra bị fail** khi thực thi, chúng tôi đã tính toán **Khoảng cách hiệu chỉnh Levenshtein (Levenshtein Edit Distance)** [80] như một thước đo đại diện để đánh giá nỗ lực thủ công cần thiết để hoàn thiện bản vá. 

Kết quả cho thấy: tính trung bình, chỉ cần thay thế **16% số lượng token** trong mã kiểm thử để biến một bản vá bị fail do GPT sinh ra trở thành bản vá chuẩn xác của lập trình viên ban đầu. **Hình 10** mô tả xu hướng giữa điểm CodeBLEU và tỷ lệ phần trăm token cần thay thế. Biểu đồ phân tán (scatter plot) cho thấy các bài kiểm thử được GPT sửa có điểm CodeBLEU càng cao thì càng đòi hỏi ít lượt chỉnh sửa token hơn, thể hiện sự tiệm cận rất gần với phiên bản sửa lỗi của nhà phát triển gốc.

Cuối cùng, để hiểu sâu hơn về hạn chế của GPT, chúng tôi đã phân tích thể loại bản vá của 11 bài kiểm thử bị fail:
- **6 bài kiểm thử** thuộc thể loại *Change Data Format*;
- Trong 5 bài còn lại: **3 bài** thuộc thể loại *Change Assertion* và **2 bài** thuộc thể loại *Change Data Structure*.

Sự áp đảo của các bài kiểm thử bị fail trong thể loại *Change Data Format* bắt nguồn từ việc thể loại này **không thể áp dụng kỹ thuật Học theo ngữ cảnh (In-Context Learning)** do không có đủ số lượng cá thể trong tập dữ liệu (như đã giải thích trong Mục III-C3). Cách tiếp cận cho thể loại này hoàn toàn chỉ dựa vào prompt kèm thông tin nhãn đơn thuần, từ đó ảnh hưởng đến chất lượng sinh mã. Tuy nhiên, như có thể thấy trong Bảng VI, đối với ba thể loại bản vá còn lại, kết quả cho thấy chất lượng sinh mã của GPT được cải thiện rất đáng kể khi triển khai in-context learning. 

Toàn bộ các bài kiểm thử được sinh ra, cùng với điểm CodeBLEU và kết quả thực thi chi tiết của chúng, đều được cung cấp công khai trong gói nhân bản (replication package) của chúng tôi.

> **Tóm tắt RQ3:** Trong tất cả các thể loại bản vá, việc cung cấp nhãn thể loại bản vá hoặc áp dụng kỹ thuật học theo ngữ cảnh (in-context learning) đều thúc đẩy đáng kể năng lực sửa bài kiểm thử flaky của mô hình GPT. Đối với hai thể loại có thể áp dụng in-context learning, kỹ thuật này mang lại kết quả vượt trội hơn so với việc chỉ cung cấp nhãn. Hơn nữa, khi cung cấp nhãn trong prompt kết hợp in-context learning, chúng tôi dự phóng rằng một tỷ lệ lớn (> 50%) các bài kiểm thử đã sửa sẽ pass thành công. Đối với những bài kiểm thử bị fail, khối lượng thay đổi cần thiết là khá hạn chế, với trung bình chỉ 16% số lượng token trong mã test cần được chỉnh sửa thêm.


---

## IV. THẢO LUẬN (DISCUSSION)

Trong phần này, thông qua việc phân tích định tính chuyên sâu, chúng tôi hướng tới việc làm sáng tỏ không chỉ cơ sở lý thuyết vững chắc mà còn cả giá trị ứng dụng thực tiễn của giải pháp được đề xuất trong việc khắc phục các bài kiểm thử flaky.

### A. Phân tích Định tính Hiệu năng của Mô hình (Qualitative Analysis of the Model's Performance)
Để hiểu rõ hơn về hiệu năng của mô hình tối ưu nhất, chúng tôi tiến hành phân tích định tính trên các bài kiểm thử flaky tiêu biểu thuộc các thể loại bản vá khác nhau.

#### 1) Kết quả Dự đoán Thể loại Bản vá của Mô hình Mã nguồn (Code Model's Prediction Results)
Trong mục này, chúng tôi phân tích các ca kiểm thử mẫu và kết quả dự đoán của mô hình **UniXcoder không dùng FSL**, vì xét trên giá trị trung bình thì đây là mô hình đạt hiệu năng tổng thể tốt nhất trong số các mô hình dự đoán. Chúng tôi đặc biệt hướng sự chú ý vào các trường hợp **Dương tính thật (True Positive - TP)** và **Âm tính giả (False Negative - FN)** trong cùng một thể loại, nhằm mang lại cho độc giả cái nhìn sâu sắc về cách các mô hình này nhận diện và dự đoán thể loại bản vá flaky. Chúng tôi cũng kiểm tra các trường hợp **Dương tính giả (False Positive - FP)**, bởi các trường hợp FP sẽ làm lãng phí thời gian của kiểm thử viên khi họ làm theo những gợi ý sai lệch, từ đó ảnh hưởng trực tiếp đến khả năng ứng dụng thực tế của phương pháp đề xuất.

##### Trường hợp Dương tính thật (True Positive - TP)
- **Hình 13** minh họa một bài kiểm thử tiêu biểu có thể loại bản vá được dự đoán chính xác là *Change Data Structure* (TP). Ở dòng thứ 2 của mã kiểm thử này, cấu trúc `HashMap` đã được sử dụng—vốn là nguyên nhân gây ra tính flaky do thứ tự duyệt phần tử không xác định, như đã thảo luận trong Mục II. Mô hình của chúng tôi đã dự đoán chính xác thể loại và đề xuất thay thế `HashMap` bằng `LinkedHashMap` để đảm bảo thứ tự các phần tử.
- Tương tự, **Hình 14(a)** thể hiện một bài kiểm thử flaky khác được mô hình dự đoán chính xác cùng lúc hai thể loại bản vá: *Handle Exception* và *Change Assertion* (TP). **Hình 14(b)** minh họa bản vá thực tế của lập trình viên cho bài test này: một khối xử lý ngoại lệ chuẩn xác đã được bổ sung, đồng thời câu lệnh `assertEquals` được chuyển đổi thành `assertJSONEqual` để xử lý so sánh các đối tượng JSON một cách chính xác mà không phụ thuộc vào thứ tự các trường trong chuỗi JSON.

##### Trường hợp Âm tính giả (False Negative - FN)
Mã kiểm thử trong **Hình 15(a)** là một ví dụ mà mô hình dự đoán của chúng tôi đã thất bại trong việc nhận diện thể loại bản vá là *Handle Exception* (FN). Ca kiểm thử này khác biệt so với các mẫu hình điển hình quan sát được trong thể loại này vì từ khóa `exception` vốn đã xuất hiện sẵn trong chữ ký của phương thức kiểm thử (method signature). Thông thường, xử lý ngoại lệ không có sẵn trong mã kiểm thử flaky mà một ngoại lệ hoặc khối `try-catch` mới được thêm vào mã để giải quyết lỗi. Tuy nhiên, ở ca kiểm thử này thì hoàn toàn ngược lại và mẫu hình này không khớp với các ví dụ khác trong tập huấn luyện. Khi kiểm tra mã kiểm thử đã sửa lỗi trong **Hình 15(b)**, chúng tôi nhận thấy phần ngoại lệ thực chất đã được gỡ bỏ như một phần của bản vá. Mặc dù vậy, công cụ gán nhãn tự động của chúng tôi đã phân loại bài test này vào nhóm xử lý ngoại lệ do sự hiện diện của từ khóa `exception`.

##### Trường hợp Dương tính giả (False Positive - FP)
Nhìn chung, chúng tôi không có nhiều trường hợp FP trong tập dữ liệu (trung bình chỉ có **13 bài test** trên cả bốn cách tiếp cận), đây là một trong những thế mạnh nổi bật của giải pháp được đề xuất. Một ví dụ về mã kiểm thử bị dự đoán FP được thể hiện trong **Hình 16**. Bài test này bị phân loại nhầm vào thể loại *Change Assertion* mặc dù trong thực tế không cần thay đổi loại assertion nào. Lý do tiềm tàng dẫn đến việc phân loại sai có thể liên quan đến một chuỗi văn bản rất dài được truyền vào câu lệnh assert trong mã nguồn. Mẫu hình sử dụng chuỗi dài này rất tương đồng với các trường hợp lỗi flaky được khắc phục bằng cách đổi sang một câu lệnh assert chuyên biệt hơn với đầu vào ngắn hơn (chẳng hạn như dùng `AssertJsonStringEquals` để xử lý chuỗi JSON). Tuy nhiên, ở đây việc sử dụng assert không đúng không phải là căn nguyên gây ra tính flaky nên nó không bị sửa đổi. Mặc dù khuyến nghị đưa ra là một FP, nhưng việc gợi ý thay đổi assertion xét cho cùng có thể không phải là một ý tưởng tồi—không phải dưới vai trò một bản sửa lỗi flaky, mà là một bước **tái cấu trúc mã (refactoring)** nhằm giúp mã kiểm thử dễ bảo trì hơn.

> **Tóm lại:** Các mô hình mã nguồn đã học một cách chuẩn xác các mẫu hình tiềm ẩn trong mã kiểm thử. Trong phần lớn các trường hợp, sự xuất hiện của FP hoặc FN chỉ đơn thuần xuất phát từ việc thiếu dữ liệu huấn luyện, nơi mà nếu không có bản vá thực tế hoặc các nguồn thông tin bổ sung khác về lỗi thì việc dự đoán chuẩn xác là bất khả thi.

---

#### 2) Bản vá Kiểm thử Flaky do GPT Sinh ra (GPT-Generated Repair of Flaky Tests)
Để xem xét kỹ lưỡng các bài kiểm thử flaky đã sửa do GPT sinh ra, chúng tôi phân tích ba phương pháp thiết kế prompt:
- **(a)** Prompt đơn giản không kèm nhãn thể loại bản vá (*Prompt Không nhãn*);
- **(b)** Cùng prompt đó nhưng được bổ sung nhãn thể loại bản vá (*Prompt Kèm nhãn*);
- **(c)** Bổ sung thêm ngữ cảnh mẫu (các ví dụ bản vá minh họa) vào prompt, tức là kỹ thuật *Học theo ngữ cảnh (In-Context Learning)* (đã mô tả trong Mục III-C3).

##### Ví dụ 1: Thể loại Thay đổi Cấu trúc Dữ liệu (Change Data Structure)
**Hình 17** mô tả một bài kiểm thử flaky (bên trái) và bản vá tương ứng do lập trình viên thực hiện (bên phải). Cả UniXcoder và CodeBERT đều phân loại chính xác bài test này thuộc thể loại bản vá *Change Data Structure*, thay thế `HashMap` bằng `LinkedHashMap` để duy trì thứ tự xuất hiện của các phần tử. 

**Hình 18** thể hiện kết quả sinh mã dựa trên hai phương pháp prompt:
- Khi mô hình được cung cấp nhãn thể loại bản vá trong prompt, đầu ra sinh ra **trùng khớp hoàn hảo 100% với bản vá của lập trình viên** (Hình 17 - bên phải), đạt điểm CodeBLEU tuyệt đối 100%.
- Ngược lại, khi không có nhãn chỉ dẫn cần sửa câu lệnh nào, mô hình đã đề xuất sửa đổi trên các câu lệnh hoàn toàn sai lệch và không hề liên quan đến nguyên nhân gây ra lỗi flaky.

##### Ví dụ 2: Thể loại Thay đổi Điều kiện (Change Condition)
Một ví dụ khác thuộc thể loại *Change Condition* được thể hiện trong **Hình 19**. Tại đây, bản vá chuẩn của lập trình viên đã sửa đổi câu lệnh `.containsExactly()` thành `.containsExactlyInAnyOrder()` để loại bỏ sự phụ thuộc vào thứ tự và triệt tiêu tính flaky. **Hình 20** thể hiện các bản vá được sinh ra khi có và không có nhãn thể loại bản vá, đồng thời minh họa bản vá khi có thêm sự chỉ dẫn từ kỹ thuật in-context learning:
- Trong cả ba trường hợp sinh mã, bản vá tạo ra đều không trùng khớp tuyệt đối 100% với bản vá của lập trình viên gốc:
  - Ở hai trường hợp đầu tiên (không nhãn và có nhãn), `.containsExactly()` đã được thay thế bằng `.containsAnyof()`—một câu lệnh tương tự với ground truth nhưng không hoàn toàn chính xác. Đáng chú ý, mô hình không kèm nhãn còn xóa nhầm khối xử lý ngoại lệ trong mã kiểm thử.
  - Khi có nhãn thể loại, mô hình đã bảo toàn được cấu trúc mã kiểm thử và nỗ lực sửa đúng vào các câu lệnh có vấn đề.
  - Ở trường hợp thứ ba (*In-Context Learning*), mô hình đã **thay thế chính xác** `.containsExactly()` bằng `.containsExactlyInAnyOrder()` dựa trên những gì mô hình học được từ các ví dụ minh họa được truyền trong prompt. Tuy nhiên, mô hình cũng vô tình loại bỏ phần xử lý ngoại lệ đúng đắn (tương tự trường hợp đầu tiên).

Dựa trên các quan sát thực nghiệm, độ chính xác của GPT trong việc sinh bản vá phụ thuộc chặt chẽ vào việc prompt có chứa nhãn thể loại bản vá hay không và số lượng ví dụ mẫu được cung cấp. Các nghiên cứu tương lai có thể tiếp tục nâng cao độ chính xác này bằng cách tăng cường dữ liệu huấn luyện và cải thiện chất lượng kỹ nghệ prompt. Toàn bộ các kết quả sinh mã chi tiết đều được chúng tôi đưa vào gói nhân bản (replication package).

---

### B. Khả năng Ứng dụng FlakyFix trong Thực tế (Application of FlakyFix in Practice?)
Trong thực tiễn kỹ nghệ phần mềm, khung làm việc FlakyFix có thể hỗ trợ sửa chữa các bài kiểm thử flaky theo cả hai hình thức: **hoàn toàn tự động** hoặc **có sự can thiệp có định hướng của con người**.

Khi một bài kiểm thử bị phát hiện và gắn cờ là có vấn đề (bởi con người hoặc bởi các công cụ phát hiện flaky tự động), lập trình viên có hai lựa chọn để loại bỏ tính flaky:
1. **Sửa đổi thủ công bởi kiểm thử viên:** Các thể loại bản vá dự đoán được cung cấp như những chỉ dẫn/gợi ý giá trị, giúp kiểm thử viên nhanh chóng khu biệt vùng mã lỗi và sửa mã kiểm thử nhanh hơn rất nhiều so với việc phải rà soát toàn bộ ca kiểm thử.
2. **Sử dụng công cụ Sửa chữa Chương trình Tự động (Automated Program Repair - APR):** Nếu một công cụ dựa trên LLM như GPT được sử dụng để tự động sửa chữa bài test, các nhãn thể loại bản vá đóng vai trò là thông tin định hướng ngữ cảnh cực kỳ đắc lực trong prompt, như đã được chứng minh thực nghiệm ở phần trước.

Tuy nhiên, như đã thảo luận trong Mục III-D3, không phải mọi bài kiểm thử do GPT sửa chữa đều đúng đắn hoàn toàn và sẽ pass ngay trong lần chạy đầu tiên. Điều này được phản ánh chân thực qua điểm CodeBLEU và kết quả chạy thực nghiệm trên tập mẫu 35 bài kiểm thử. Dẫu vậy, chúng tôi ước tính rằng:
- **Đại đa số các ca kiểm thử do GPT sửa chữa (> 50% đến 83%) dự kiến sẽ pass thành công**, với tỷ lệ cụ thể phụ thuộc vào dạng prompt được áp dụng.
- Đối với những bài kiểm thử sinh ra bị fail khi chạy thực tế, chúng sẽ đòi hỏi một mức độ can thiệp thủ công nhất định từ kiểm thử viên để có thể pass hoàn toàn. Phân tích của chúng tôi thông qua khoảng cách hiệu chỉnh Levenshtein cho thấy: **trung bình chỉ cần sửa đổi 16% số lượng token** trong một bài test bị fail để biến nó thành bản vá chuẩn xác tương đương với lập trình viên gốc.

Do đó, việc khắc phục hoàn toàn các bài kiểm thử flaky vẫn đòi hỏi một mức độ nỗ lực nhất định của con người đối với một thiểu số các ca kiểm thử, và quá trình này không hoàn toàn "miễn phí". Tuy nhiên, với sự phát triển nhanh chóng của các thế hệ GPT mới hơn và các kỹ thuật thiết kế prompt tiên tiến hơn, chúng ta hoàn toàn có thể kỳ vọng vào những bản vá ngày càng đáng tin cậy hơn và tỷ lệ bài test pass cao hơn nữa trong tương lai.


---

## V. CÁC MỐI ĐE DỌA ĐẾN TÍNH HỢP LỆ (THREATS TO VALIDITY)

### A. Tính Hợp lệ trong Xây dựng (Construct Threats)
Trong nghiên cứu của chúng tôi, mối đe dọa tiềm tàng chính đối với tính hợp lệ trong xây dựng là khả năng định nghĩa các nhãn thể loại bản vá không chính xác hoặc không đầy đủ trong câu hỏi RQ1, từ đó có thể làm suy giảm độ tin cậy của các kết quả trong RQ2 và RQ3. Để giảm thiểu mối đe dọa này:
1. Trước tiên, chúng tôi đã hệ thống hóa và tự động hóa quy trình gán nhãn thông qua các bộ quy tắc phỏng đoán (heuristics) công khai trong gói nhân bản để cộng đồng có thể đánh giá và cải tiến sâu hơn;
2. Chúng tôi cũng tiến hành kiểm tra thủ công các mẫu ngẫu nhiên của các bài kiểm thử đã gán nhãn nhằm xác thực tính chính xác của quy trình;
3. Hơn nữa, độ chính xác của các nhãn thể loại bản vá được dự đoán là rất cao trên hầu hết các thể loại, như thể hiện trong Bảng III. Nhờ đó, chúng tôi đảm bảo rằng các nhãn dự đoán chuẩn xác được đưa vào các dạng prompt khác nhau cho LLM trong RQ3.

Đối với RQ2, chúng tôi đã không thực hiện phân tích riêng rẽ theo từng dự án (per-project analysis) do số lượng các cá thể dương tính cho từng thể loại bản vá bị hạn chế trong khi số lượng dự án trong tập dữ liệu lại rất lớn (96 dự án). Điều này đồng nghĩa với việc đối với mỗi bài test flaky trong tập kiểm thử, chỉ có rất ít bài test flaky từ cùng một dự án xuất hiện trong tập huấn luyện, đặc biệt là đối với một thể loại cụ thể. Do đó, chúng tôi báo cáo kết quả tổng thể trên tất cả các dự án.

Liên quan đến các độ đo đánh giá trong RQ3, chúng tôi đã sử dụng điểm CodeBLEU—một chỉ số phổ biến trong các tác vụ sinh mã nguồn. Tuy nhiên, chúng tôi không thể thực thi toàn bộ các bài kiểm thử được sinh tự động này để kiểm tra chức năng của chúng. Do sự phụ thuộc phức tạp vào môi trường và thư viện trong các dự án mã nguồn mở, việc biên dịch và chạy toàn bộ các bài test này đòi hỏi chi phí tính toán và thời gian rất lớn. Do đó, chúng tôi chưa thể khẳng định liệu tất cả các bài test có điểm CodeBLEU cao có pass trên thực tế hay không, hoặc thậm chí liệu chúng có thể thực thi được hay không. Mặc dù vậy, sự cải thiện về điểm CodeBLEU hầu như không thể tạo ra các ca kiểm thử tồi hơn về mặt chức năng hoặc khả năng thực thi. Dẫu sao, sự thiếu hụt của các độ đo đánh giá chất lượng sinh mã hiện tại vẫn là một thách thức đã được thừa nhận rộng rãi [84] trong lĩnh vực này và cần thêm các nghiên cứu tương lai để thu hẹp mối đe dọa đó.

### B. Tính Hợp lệ Nội tại (Internal Threats)
Tính hợp lệ nội tại liên quan đến việc đảm bảo rằng mối quan hệ nguyên nhân - kết quả được xác định trong nghiên cứu thực sự tồn tại mà không bị chi phối bởi các yếu tố gây nhiễu (confounding factors). Trong nghiên cứu này, luận điểm cốt lõi là: *các thể loại bản vá dự đoán của chúng tôi sẽ hỗ trợ đắc lực trong việc sửa chữa lỗi flaky*. Yếu tố gây nhiễu chính nằm ở cách thức chúng tôi thiết kế prompt cho mô hình GPT-3.5 khi yêu cầu sửa lỗi bài test. Kết quả tốt hơn có thể đạt được trong tương lai với sự chỉ dẫn chi tiết hơn và nhiều ví dụ minh họa hơn trong prompt. Tương tự, việc sử dụng các mô hình mạnh mẽ hơn như GPT-4 có thể mang lại kết quả cao hơn nữa, nhưng như đã thảo luận trong Mục II-C, điều này có thể làm dấy lên rủi ro rò rỉ dữ liệu (data leakage) đối với tập dữ liệu của chúng tôi.

Ngoài ra, sẽ rất có giá trị nếu phân tích được tần suất GPT sinh ra bản vá đúng khi tiếp nhận một nhãn thể loại bản vá bị dự đoán sai. Tuy nhiên, như đã giải thích trong Mục III-B5, chúng tôi bị giới hạn ở việc chỉ có thể thực thi 35 bài kiểm thử. Trong tập 35 ca kiểm thử thực thi được này, chúng tôi chỉ bắt gặp duy nhất một trường hợp mà thể loại bản vá bị dự đoán sai (và ngay cả trường hợp đó cũng đúng một phần vì một trong hai thể loại đã được dự đoán chính xác). Do đó, việc thực hiện phân tích này một cách đáng tin cậy là chưa khả thi với tập dữ liệu hiện tại.

Một mối đe dọa nội tại khác khi dự đoán nhãn là **kích thước ngữ cảnh (context size)** của các mô hình mã nguồn (510 token đối với CodeBERT và 1022 token đối với UniXcoder). Giới hạn này có thể cắt bớt mã nguồn của một số ca kiểm thử dài và dẫn đến mất mát thông tin. Trong tập dữ liệu của chúng tôi, có **49 bài test (chiếm 11% trong tổng số 562 bài test flaky)** vượt quá giới hạn 510 token, và **17 bài test (4%)** vượt quá 1022 token. Điều này có thể ảnh hưởng tiềm tàng đến độ chính xác dự đoán, đặc biệt là đối với những thể loại bản vá có số lượng mẫu dương tính hạn chế. Các nghiên cứu sâu hơn cần phân tích mức độ tác động của hạn chế này lên kết quả nghiên cứu.

### C. Tính Hợp lệ của Kết luận (Conclusion Threats)
Để giảm thiểu các mối đe dọa đối với tính hợp lệ của kết luận, trong RQ2 chúng tôi đã sử dụng Kiểm định Fisher chính xác (Fisher's Exact Test) nhằm đảm bảo các kết luận rút ra có ý nghĩa thống kê. Chúng tôi cũng áp dụng kiểm định phi tham số Wilcoxon signed-rank test khi so sánh giữa các loại prompt khác nhau trong RQ3.

Tuy nhiên, vẫn tồn tại mối đe dọa tiềm tàng trong kết quả RQ3 bắt nguồn từ **tính ngẫu nhiên cố hữu (inherent randomness)** của các mô hình GPT. Thực tế cho thấy, việc sử dụng cùng một mô hình và cùng một prompt có thể tạo ra các kết quả đầu ra khác nhau khi sử dụng nhiệt độ (temperature) cao hơn. Nhìn chung, lĩnh vực kỹ nghệ prompt—bao gồm cả việc tối ưu hóa đầu ra qua nhiều vòng tương tác—vẫn là một lĩnh vực tương đối mới mẻ và hiện còn thiếu các chỉ dẫn chuẩn mực, chính xác và đáng tin cậy trong y văn. Các nghiên cứu tiếp theo sẽ tiếp tục khảo sát các chiến lược prompt mới khi chúng xuất hiện.

### D. Tính Hợp lệ Bên ngoài (External Threats)
Công cụ gán nhãn tự động và các quy tắc phỏng đoán (heuristics) của chúng tôi hiện được định nghĩa chuyên biệt cho các bài kiểm thử bằng ngôn ngữ **Java**. Chúng tôi chưa đánh giá công cụ trên các ngôn ngữ lập trình khác, tuy nhiên phương pháp này hoàn toàn có thể thích ứng với các ngôn ngữ khác và các dự án mới bằng cách tích hợp các từ khóa và quy tắc cú pháp tương ứng. Thêm vào đó, cả ba mô hình CodeBERT, UniXcoder và GPT đều đã được tiền huấn luyện trên đa ngôn ngữ lập trình, tạo nền tảng vững chắc cho việc mở rộng sang các hệ sinh thái khác.

---

## VI. CÁC CÔNG TRÌNH LIÊN QUAN (RELATED WORK)

Trong phần này, chúng tôi cung cấp cái nhìn tổng quan về các công trình nghiên cứu có liên quan mật thiết nhất đến bài toán dự đoán thể loại bản vá và sửa chữa bài kiểm thử flaky. 

Có hai hướng nghiên cứu mà chúng tôi chủ động loại trừ vì ít liên quan trực tiếp đến phạm vi bài báo:
1. **Các nghiên cứu sửa lỗi chương trình nói chung (Generic Program Repair - APR) [85]:** Mặc dù việc sửa mã kiểm thử có thể coi là tương tự bài toán sửa lỗi chương trình, nhưng giữa hai bài toán tồn tại những khác biệt nền tảng bắt nguồn từ các mẫu hình bản vá (fix patterns). Bản vá lỗi mã nguồn nói chung có thể xuất hiện dưới vô vàn hình thái và mẫu hình phong phú, khiến việc dự đoán thể loại bản vá trở thành một nhiệm vụ cực kỳ khó khăn. Thêm vào đó, dữ liệu dành cho sửa lỗi chương trình tổng quát phong phú hơn rất nhiều (về mặt lý thuyết là bất kỳ commit sửa code nào trên GitHub) so với dữ liệu sửa lỗi flaky test. Vì vậy, chúng tôi không đi sâu vào từng bài báo nghiên cứu APR tổng quát.
2. **Các nghiên cứu phân tích "mùi" kiểm thử (Test Smells) [86]:** Mặc dù các công trình này liên quan đến các vấn đề trong mã kiểm thử, nhưng chúng mang tính chất chung về chất lượng thiết kế mã nguồn mà không trực tiếp liên quan đến hiện tượng kiểm thử chập chờn (flakiness).

---

### A. Phân loại Thể loại Bản vá và Mẫu hình Sửa lỗi
Nhóm công trình liên quan đầu tiên tập trung vào việc xây dựng phân loại (taxonomy) hoặc thể loại của các bản vá lỗi mã nguồn. Mặc dù không nghiên cứu về flaky test hay thậm chí không nghiên cứu trên mã kiểm thử, những nghiên cứu này giải quyết bài toán tương đồng: phân loại và dự đoán các bản sửa lỗi hoặc nguyên nhân lỗi.

Ni et al. [71] đề xuất cách tiếp cận phân loại các thể loại sửa lỗi phần mềm sử dụng Mạng nơ-ron Tích chập dựa trên Cây cú pháp (TBCNN). Họ sử dụng mã diff trước và sau khi sửa lỗi ở cấp độ Cây Cú pháp Trừu tượng (AST) để xây dựng cây bản vá (fix trees) làm đầu vào cho mô hình TBCNN. Ngược lại hoàn toàn, **mục tiêu của FlakyFix là phát triển một bộ phân loại thể loại bản vá chỉ dựa duy nhất vào mã kiểm thử flaky ban đầu**, hoàn toàn không phụ thuộc vào phiên bản đã sửa lỗi hay mã nguồn sản phẩm (production code).

---

### B. Dự đoán Nguyên nhân Gây ra Tính Flaky
Dự đoán nguyên nhân gốc rễ (root cause) của flaky test là một hướng tiếp cận có liên quan chặt chẽ đến nghiên cứu của chúng tôi.

Akli et al. [23] đề xuất công cụ **FlakyCat** để phân loại các bài test flaky dựa trên nguyên nhân gốc rễ sử dụng CodeBERT và kỹ thuật Học ít mẫu (FSL). Họ gán nhãn thủ công cho 343 bài test flaky theo 10 thể loại nguyên nhân được gợi ý bởi Luo et al. [1] và Eck et al. [63]. Tuy nhiên, họ chỉ báo cáo kết quả dự đoán cho đúng 4 thể loại nguyên nhân (*Async wait*, *Concurrency*, *Time*, và *Unordered collection*) do thiếu các ví dụ dương tính để huấn luyện bộ phân loại học máy cho các thể loại khác. Họ đạt kết quả cao nhất ở thể loại nguyên nhân *Unordered collection*, với Precision 85% và Recall 80%.

Trong một khảo sát gần đây về flaky test [19], [87], Parry et al. đã ánh xạ ba nguyên nhân gây lỗi flaky khác nhau với các giải pháp sửa lỗi tiềm năng. Chẳng hạn, họ gợi ý thêm hoặc sửa đổi các câu lệnh assertion để khắc phục lỗi flaky do bất đồng bộ/đồng thời gây ra. 

> **Ưu thế vượt trội của việc dự đoán Thể loại Bản vá:** Việc dự đoán thể loại bản vá mang lại cho kiểm thử viên một **định hướng hành động cụ thể** để chỉnh sửa mã nguồn. Biết rằng "bất đồng bộ" đang gây ra lỗi flaky trong một bài test không thực sự hữu ích ngay cho kiểm thử viên, vì họ vẫn không biết đoạn mã nào trong ca test đang gây chuyện. Tuy nhiên, nếu biết rằng **"thay đổi assertion"** hoặc **"thay đổi cấu trúc dữ liệu"** có thể loại bỏ lỗi flaky, họ sẽ nhận được chỉ dẫn thực tế và có tính hành động cao hơn rất nhiều.

Các nhà nghiên cứu khác [39], [87] đã tiến hành các nghiên cứu thực nghiệm nhằm nhận diện nguyên nhân, tác động và các chiến lược hiện có để giảm thiểu lỗi flaky. Tuy nhiên, chưa có công trình nào nỗ lực phân loại các bài kiểm thử flaky dựa trên chính bản vá của chúng.

Nghiên cứu về sửa chữa lỗi flaky và phân loại thể loại bản vá hiện vẫn đang ở giai đoạn sơ khai, với phần lớn các công trình tập trung vào sửa các bài test flaky phụ thuộc vào thứ tự thực thi (Order-Dependent - OD):
- **iPFlakies** [64] và **iFixFlakies** [35] đề xuất các phương pháp giải quyết lỗi flaky phụ thuộc thứ tự;
- **FLEX** [62] tự động sửa chữa các bài test flaky gây ra bởi tính ngẫu nhiên thuật toán trong các thuật toán học máy (ML algorithms);
- **TRaf** [40] tập trung sửa chữa bài test flaky do thời gian chờ bất đồng bộ trong kiểm thử web;
- Parry et al. [20] đề xuất một nghiên cứu định nghĩa các thể loại bản vá flaky khác nhau và phân loại 75 commit flaky dựa trên các thể loại này. Tuy nhiên, việc phân loại hoàn toàn được thực hiện thông qua **rà soát thủ công** các commit, mã diff, bình luận của lập trình viên và các issue bên ngoài phạm vi mã kiểm thử;
- Trong một nghiên cứu khác trên cơ sở dữ liệu của Mozilla [63], các bài test được phân loại dựa trên nguồn gốc (nguyên nhân nằm ở mã nguồn hay mã kiểm thử) và nỗ lực của lập trình viên để sửa chúng;
- Sự cần thiết cấp bách của việc sửa chữa tự động các bài kiểm thử flaky và thực hiện các bản vá nhỏ nhanh chóng đã được nhấn mạnh mạnh mẽ trong khảo sát của Gruber và Fraser [88].

Nghiên cứu của chúng tôi giải quyết trọn vẹn những khoảng trống này bằng cách: phát triển một giải pháp tự động để phân loại các bài test flaky dựa trên các thể loại bản vá được định nghĩa chặt chẽ, chỉ dựa duy nhất vào mã kiểm thử, cung cấp hướng dẫn thực tiễn cho cả việc sửa chữa thủ công và tự động. Chúng tôi cũng cung cấp một công cụ tự động gán nhãn để huấn luyện các mô hình dự đoán theo ngữ cảnh cụ thể.

---

### C. Ứng dụng Mô hình Ngôn ngữ Lớn (LLM) trong Sửa lỗi Chương trình Tự động
Mặc dù chúng tôi không rà soát toàn bộ tài liệu APR tổng quát, chúng tôi thảo luận về các công trình sử dụng LLM cho việc tự động sửa lỗi chương trình, vì hướng nghiên cứu này có liên quan trực tiếp về mặt kỹ thuật với câu hỏi RQ3.

Những bước tiến nhảy vọt gần đây của các LLM như ChatGPT [57], Copilot [89] và các mô hình chuyên biệt cho mã nguồn đã thúc đẩy mạnh mẽ lĩnh vực này. Các mô hình này thể hiện năng lực vượt trội trong việc sinh mã nguồn và thu hút sự quan tâm lớn từ giới nghiên cứu APR:
- Ribeiro et al. [90] sử dụng GPT-3 để tự động khắc phục các lỗi trong 1.318 chương trình OCaml, đạt tỷ lệ sửa lỗi thành công 39%;
- Julian et al. [91] sử dụng mô hình Codex của OpenAI để sửa lỗi trong các chương trình Java và Python, nhận thấy tỷ lệ sửa lỗi cao hơn trên Python. Việc kết hợp prompt và gợi ý đã cải thiện khả năng định vị lỗi của Codex trên các chương trình Java;
- Chunqiu et al. [92] khảo sát các mô hình LLM khác nhau như Codex, InCoder, CodeT5 và GPT-2 cho bài toán sửa lỗi chương trình trên Java, Python và C;
- Mashhadi et al. [76] và Xia et al. [93] ứng dụng CodeBERT cho việc sửa lỗi chương trình tự động trên các tập dữ liệu như ManySStuBs4J và Defects4J, đạt kết quả state-of-the-art đối với các phân đoạn mã ngắn do giới hạn đầu vào 512 token của CodeBERT.

> **Đóng góp Độc nhất của FlakyFix:** Trong khi các nghiên cứu hiện tại hầu như chỉ tập trung vào việc khắc phục lỗi trong mã nguồn sản phẩm (production code), **rất ít sự chú ý được dành cho việc giải quyết tính flaky tiềm ẩn bên trong chính mã kiểm thử**. Nghiên cứu của chúng tôi đánh dấu nỗ lực đầu tiên trong việc tự động hóa hoàn toàn quy trình sửa chữa bài kiểm thử flaky bằng GPT, được tăng cường sức mạnh thông qua việc cung cấp thông tin thể loại bản vá dự đoán để khu biệt chính xác các câu lệnh liên quan đến lỗi flaky trong mã nguồn.

---

## VII. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN TƯƠNG LAI (CONCLUSION AND FUTURE WORK)

Trong bài báo này, chúng tôi đã đề xuất một khung làm việc toàn diện nhằm:
1. Phân loại các bài kiểm thử flaky theo các thể loại bản vá có giá trị thực tiễn cao, dựa duy nhất trên mã kiểm thử gốc;
2. Tận dụng thông tin thể loại bản vá này để sinh ra các bản sửa lỗi hoàn toàn tự động cho bài kiểm thử flaky bằng các mô hình ngôn ngữ.

Xét trong bối cảnh các bộ dữ liệu mã nguồn mở phục vụ nghiên cứu flaky test còn vô cùng khan hiếm, tập dữ liệu được gán nhãn tự động mà chúng tôi xây dựng sẽ là một tài nguyên quý giá cho cộng đồng nghiên cứu tương lai, đặc biệt là trong lĩnh vực dự đoán và sửa chữa flaky test bằng học máy.

Chúng tôi đã đánh giá hai mô hình mã nguồn tiền huấn luyện là **CodeBERT** và **UniXcoder**, cả khi có và không có kỹ thuật Học ít mẫu (Few-Shot Learning), và nhận thấy mô hình **UniXcoder vượt trội hơn CodeBERT** trong việc dự đoán hầu hết các thể loại bản vá. Chúng tôi cũng chứng minh rằng thông tin thể loại bản vá, khi được bổ trợ bởi kỹ thuật **Học theo ngữ cảnh (In-Context Learning)**, có thể hỗ trợ đắc lực cho một mô hình ngôn ngữ lớn (ở đây là **GPT-3.5 Turbo**) trong việc sửa chữa mã kiểm thử flaky hiệu quả hơn rõ rệt.

Cuối cùng, chúng tôi đã thực thi một tập mẫu các bài test flaky do GPT sửa chữa và ước tính rằng một tỷ lệ lớn (xấp xỉ từ **51% đến 83%**) các bài test này có thể kỳ vọng sẽ pass thành công. Đối với những bài test sinh ra bị fail, trung bình chỉ cần chỉnh sửa thêm **16% số lượng token** trong mã kiểm thử để chúng có thể pass hoàn toàn.

### Hướng Nghiên cứu Tương lai:
- Mở rộng tập dữ liệu flaky test với quy mô lớn hơn;
- Mở rộng các quy tắc phỏng đoán (heuristics) gán nhãn tự động sang các ngôn ngữ lập trình phổ biến khác;
- Tái lập và nhân bản nghiên cứu với các mô hình LLM tiên tiến hơn (chẳng hạn như GPT-4 hoặc Claude);
- Phát triển các phương pháp tiếp cận nhẹ (lightweight) và có khả năng mở rộng (scalable) để truy cập và sửa đổi mã nguồn sản phẩm (production code) đối với những bài test flaky bắt nguồn từ lỗi của hệ thống chính.

---

## TUYÊN BỐ VỀ TÍNH KHẢ DỤNG CỦA DỮ LIỆU (DATA AVAILABILITY STATEMENT)
Các thực nghiệm được tiến hành trong công trình nghiên cứu này được hỗ trợ một phần bởi **WestGrid** (https://www.westgrid.ca) và **Compute Canada** (https://www.computecanada.ca). Toàn bộ mã nguồn, dữ liệu thực nghiệm, kịch bản gán nhãn và kết quả sinh mã chi tiết được công khai phục vụ tái tạo tại:
- Kho lưu trữ Figshare: `https://figshare.com/s/47f0fb6207ac3f9e2351`
- Gói nhân bản mã nguồn mở: `https://github.com/nanda-lab/FlakyFix`

---

## TÀI LIỆU THAM KHẢO (REFERENCES)

[1] Q. Luo, F. Hariri, L. Eloussi, and D. Marinov, “An empirical analysis of flaky tests,” in *Proc. 22nd ACM SIGSOFT Int. Symp. Found. Softw. Eng.*, 2014, pp. 643–653.

[2] E. Fallahzadeh and P. C. Rigby, “The impact of flaky tests on historical test prioritization on chrome,” in *Proc. 44th Int. Conf. Softw. Eng.: Softw. Eng. Pract.*, 2022, pp. 273–282.

[3] B. Harry, “How we approach testing VSTS to enable continuous delivery,” 2019. [Online]. Available: https://devblogs.microsoft.com/bharry/testing-in-a-cloud-delivery-cadence/

[4] M. Cordy, R. Rwemalika, M. Papadakis, and M. Harman, “FlakiMe: Laboratory-controlled test flakiness impact assessment. A case study on mutation testing and program repair,” 2019, arXiv:1912.03197.

[5] W. Lam, S. Winter, A. Wei, T. Xie, D. Marinov, and J. Bell, “A large-scale longitudinal study of flaky tests,” *Proc. ACM Program. Lang.*, vol. 4, no. OOPSLA, pp. 1–29, 2020.

[6] S. Habchi, G. Haben, M. Papadakis, M. Cordy, and Y. L. Traon, “A qualitative study on the sources, impacts, and mitigation strategies of flaky tests,” in *Proc. IEEE Conf. Softw. Testing, Verification Validation (ICST)*, Piscataway, NJ, USA: IEEE Press, 2022, pp. 244–255.

[7] A. Ahmad, F. G. Oliveira Neto, Z. Shi, K. Sandahl, and O. Leifler, “A multi-factor approach for flaky test detection and automated root cause analysis,” in *Proc. 28th Asia-Pacific Softw. Eng. Conf. (APSEC)*, Piscataway, NJ, USA: IEEE Press, 2021, pp. 338–348.

[8] R. Verdecchia, E. Cruciani, B. Miranda, and A. Bertolino, “Know you neighbor: Fast static prediction of test flakiness,” *IEEE Access*, vol. 9, pp. 76119–76134, 2021.

[9] V. Pontillo, F. Palomba, and F. Ferrucci, “Toward static test flakiness prediction: A feasibility study,” in *Proc. 5th Int. Workshop Mach. Learn. Techn. Softw. Qual. Evol.*, 2021, pp. 19–24.

[10] J. Bell, O. Legunsen, M. Hilton, L. Eloussi, T. Yung, and D. Marinov, “DeFlaker: Automatically detecting flaky tests,” in *Proc. 40th Int. Conf. Softw. Eng.*, 2018, pp. 433–444.

[11] Y. Qin et al., “Peeler: Learning to effectively predict flakiness without running tests,” in *Proc. IEEE Int. Conf. Softw. Maintenance Evol. (ICSME)*, Piscataway, NJ, USA: IEEE Press, 2022, pp. 257–268.

[12] S. Fatima, T. A. Ghaleb, and L. Briand, “Flakify: A black-box, language model-based predictor for flaky tests,” *IEEE Trans. Softw. Eng.*, vol. 49, no. 4, pp. 1912–1927, Apr. 2023.

[13] M. Gruber, M. Heine, N. Oster, M. Philippsen, and G. Fraser, “Practical flaky test prediction using common code evolution and test history data,” in *Proc. IEEE Conf. Softw. Testing, Verification Validation (ICST)*, Piscataway, NJ, USA: IEEE Press, 2023, pp. 210–221.

[14] A. Alshammari, C. Morris, M. Hilton, and J. Bell, “FlakeFlagger: Predicting flakiness without rerunning tests,” in *Proc. IEEE/ACM 43rd Int. Conf. Softw. Eng. (ICSE)*, Piscataway, NJ, USA: IEEE Press, 2021, pp. 1572–1584.

[15] G. Pinto, B. Miranda, S. Dissanayake, M. d’Amorim, C. Treude, and A. Bertolino, “What is the vocabulary of flaky tests?” in *Proc. 17th Int. Conf. Mining Softw. Repositories*, 2020, pp. 492–502.

[16] G. Haben, S. Habchi, M. Papadakis, M. Cordy, and Y. L. Traon, “A replication study on the usability of code vocabulary in predicting flaky tests,” in *Proc. IEEE/ACM 18th Int. Conf. Mining Softw. Repositories (MSR)*, Piscataway, NJ, USA: IEEE Press, 2021, pp. 219–229.

[17] B. H. P. Camara, M. Auré, G. Silva, A. T. Endo, and S. R. Vergilio, “What is the vocabulary of flaky tests? An extended replication,” in *Proc. IEEE/ACM 29th Int. Conf. Program Comprehension (ICPC)*, Piscataway, NJ, USA: IEEE Press, 2021, pp. 444–454.

[18] A. Ahmad, “An evaluation of machine learning methods for predicting flaky tests,” in *Proc. 27th Asia-Pacific Softw. Eng. Conf. (APSEC)*, Singapore, Dec. 2020, pp. 3–9.

[19] O. Parry, G. M. Kapfhammer, M. Hilton, and P. McMinn, “A survey of flaky tests,” *ACM Trans. Softw. Eng. Methodol.*, vol. 31, no. 1, pp. 1–74, 2021.

[20] O. Parry, G. M. Kapfhammer, M. Hilton, and P. McMinn, “What do developer-repaired flaky tests tell us about the effectiveness of automated flaky test detection?” in *Proc. 3rd ACM/IEEE Int. Conf. Automat. Softw. Test*, 2022, pp. 160–164.

[21] N. Hashemi, A. Tahir, and S. Rasheed, “An empirical study of flaky tests in JavaScript,” in *Proc. IEEE Int. Conf. Softw. Maintenance Evol. (ICSME)*, Piscataway, NJ, USA: IEEE Press, 2022, pp. 24–34.

[22] W. Lam, “International dataset of flaky tests (IDoFT),” 2020. [Online]. Available: https://github.com/TestingResearchIllinois/idoft

[23] A. Akli, G. Haben, S. Habchi, M. Papadakis, and Y. L. Traon, “FlakyCat: Predicting flaky tests categories using few-shot learning,” in *Proc. IEEE/ACM Int. Conf. Automat. Softw. Test (AST)*, Piscataway, NJ, USA: IEEE Press, 2023, pp. 140–151.

[24] K. Wing Lam, M. vanç, H. S. lu, and S. Thummalapenta, “A study on the lifecycle of flaky tests,” in *Proc. ACM/IEEE 42nd Int. Conf. Softw. Eng.*, 2020, pp. 1471–1482.

[25] Z. Feng et al., “CodeBERT: A pre-trained model for programming and natural languages,” 2020, arXiv:2002.08155.

[26] D. Guo et al., “UniXcoder: Unified cross-modal pre-training for code representation,” 2022, arXiv:2203.03850.

[27] Y. Wang, Q. Yao, J. T. Kwok, and L. M. Ni, “Generalizing from a few examples: A survey on few-shot learning,” *ACM Comput. Surveys*, vol. 53, no. 3, pp. 1–34, 2020.

[28] R. OpenAI, “GPT-4 technical report,” 2023, arxiv:2303.08774.

[29] Y. Dong, J. Ding, X. Jiang, Z. Li, G. Li, and Z. Jin, “Code-Score: Evaluating code generation by learning code execution,” 2023, arXiv:2301.09043.

[30] J. Liu, D. Shen, Y. Zhang, B. Dolan, L. Carin, and W. Chen, “What makes good in-context examples for GPT-3?” 2021, arXiv:2101.06804.

[31] A. Wei, P. Yi, T. Xie, D. Marinov, and W. Lam, “Probabilistic and systematic coverage of consecutive test-method pairs for detecting order-dependent flaky tests,” in *Proc. Tools Algorithms Construction Anal. Syst.: 27th Int. Conf., (TACAS)*, Luxembourg City, Luxembourg, Springer, Mar. 2013, pp. 270–287.

[32] W. Lam, R. Oei, A. Shi, D. Marinov, and T. Xie, “iDFlakies: A framework for detecting and partially classifying flaky tests,” in *Proc. 12th IEEE Conf. Softw. Testing, Validation Verification*, Piscataway, NJ, USA: IEEE Press, 2019, pp. 312–322.

[33] W. Lam, S. Winter, A. Astorga, V. Stodden, and D. Marinov, “Understanding reproducibility and characteristics of flaky tests through test reruns in Java projects,” in *Proc. IEEE 31st Int. Symp. Softw. Rel. Eng. (ISSRE)*, Piscataway, NJ, USA: IEEE Press, 2020, pp. 403–413.

[34] W. Lam, A. Shi, R. Oei, S. Zhang, M. D. Ernst, and T. Xie, “Dependent-test-aware regression testing techniques,” in *Proc. 29th ACM SIGSOFT Int. Symp. Softw. Testing Anal.*, 2020, pp. 298–311.

[35] A. Shi, W. Lam, R. Oei, T. Xie, and D. Marinov, “iFixFlakies: A framework for automatically fixing order-dependent flaky tests,” in *Proc. 27th ACM Joint Meeting Eur. Softw. Eng. Conf. Symp. Found. Softw. Eng.*, 2019, pp. 545–555.

[36] M. L. McHugh, “Interrater reliability: The kappa statistic,” *Biochemia Medica*, vol. 22, no. 3, pp. 276–282, 2012.

[37] G. Meszaros, *xUnit Test Patterns: Refactoring Test Code*. London, U.K.: Pearson Education, 2007.

[38] R. Osherove, *The Art of Unit Testing: With Examples in C#*. Simon and Schuster, Shelter Island, New York, USA: Manning, 2013.

[39] W. Zheng, G. Liu, M. Zhang, X. Chen, and W. Zhao, “Research progress of flaky tests,” in *Proc. IEEE Int. Conf. Softw. Anal., Evol. Reeng. (SANER)*, Piscataway, NJ, USA: IEEE Press, 2021, pp. 639–646.

[40] Y. Pei, J. Sohn, S. Habchi, and M. Papadakis, “TRaf: Time-based repair for asynchronous wait flaky tests in web testing,” 2023, arXiv:2305.08592.

[41] C. Niu, C. Li, V. Ng, D. Chen, J. Ge, and B. Luo, “An empirical comparison of pre-trained models of source code,” 2023, arXiv:2302.04026.

[42] W. X. Zhao et al., “A survey of large language models,” 2023, arXiv:2303.18223.

[43] R. Sennrich, B. Haddow, and A. Birch, “Neural machine translation of rare words with subword units,” 2015, arXiv:1508.07909.

[44] A. He, C. Luo, X. Tian, and W. Zeng, “A twofold Siamese network for real-time object tracking,” in *Proc. IEEE Conf. Comput. Vis. Pattern Recognit.*, 2018, pp. 4834–4843.

[45] F. Schroff, D. Kalenichenko, and J. Philbin, “FaceNet: A unified embedding for face recognition and clustering,” in *Proc. IEEE Conf. Comput. Vis. Pattern Recognit.*, 2015, pp. 815–823.

[46] P. Neculoiu, M. Versteegh, and M. Rotaru, “Learning text similarity with Siamese recurrent networks,” in *Proc. 1st Workshop Representation Learn. NLP*, 2016, pp. 148–157.

[47] G. Koch, R. Zemel, and R. Salakhutdinov, “Siamese neural networks for one-shot image recognition,” in *Proc. ICML Deep Learn. Workshop*, vol. 2, 2015, pp. 3–7.

[48] J. Mueller and A. Thyagarajan, “Siamese recurrent architectures for learning sentence similarity,” in *Proc. AAAI Conf. Artif. Intell.*, vol. 30, 2016, pp. 2–6.

[49] S. E. Anigri, M. M. Himmi, and A. Mahmoudi, “How BERT’s dropout fine-tuning affects text classification?” in *Proc. Int. Conf. Bus. Intell.*, Springer, 2021, pp. 130–139.

[50] Z. Yao, A. Gholami, S. Shen, M. Mustafa, K. Keutzer, and M. Mahoney, “ADAHESSIAN: An adaptive second order optimizer for machine learning,” in *Proc. AAAI Conf. Artif. Intell.*, vol. 35, 2021, pp. 10665–10673.

[51] A. F. Agarap, “Deep learning using rectified linear units,” 2018, arXiv:1803.08375.

[52] Z. Zheng et al., “A survey of large language models for code: Evolution, benchmarking, and future trends,” 2023, arXiv:2311.10372.

[53] A. Fan et al., “Large language models for software engineering: Survey and open problems,” 2023, arXiv:2310.03533.

[54] H. Pearce, B. Tan, B. Ahmad, R. Karri, and B. Dolan-Gavitt, “Examining zero-shot vulnerability repair with large language models,” in *Proc. IEEE Symp. Secur. Privacy (SP)*, Piscataway, NJ, USA: IEEE Press, 2023, pp. 2339–2356.

[55] J. White, S. Hays, Q. Fu, J. Spencer-Smith, and D. C. Schmidt, “Chatgpt prompt patterns for improving code quality, refactoring, requirements elicitation, and software design,” 2023, arXiv:2303.07839.

[56] Q. Zhang et al., “A critical review of large language model on software engineering,” 2023, arXiv:2310.08879.

[57] M. Fu, C. Tantithamthavorn, Nguyen, and T. Le, “ChatGPT for vulnerability detection, classification, and repair,” 2023, arXiv:2310.09810.

[58] “OpenAI platform documentation: Continuous model upgrades,” OpenAI. Accessed: 2023. [Online]. Available: https://platform.openai.com/docs/overview

[59] S. Min et al., “Rethinking the Role of Demonstrations: What Makes In-Context Learning Work?” in *Proc. Conf. Empirical Methods Nat. Lang. Process.*, 2022, arXiv:2202.12837.

[60] S. Qiao et al., “Reasoning with language model prompting: A survey,” 2022, arXiv:2212.09597.

[61] T. Brown et al., “Language models are few-shot learners,” in *Proc. Adv. Neural Inf. Process. Syst.*, vol. 33, 2020, pp. 1877–1901.

[62] S. Dutta, A. Shi, and S. Misailovic, “FLEX: Fixing flaky tests in machine learning projects by updating assertion bounds,” in *Proc. 29th ACM Joint Meeting Eur. Softw. Eng. Conf. Symp. Found. Softw. Eng.*, 2021, pp. 603–614.

[63] M. Eck, F. Palomba, M. Castelluccio, and A. Bacchelli, “Understanding flaky tests: The developer’s perspective,” in *Proc. 27th ACM Joint Meeting Eur. Softw. Eng. Conf. Symp. Found. Softw. Eng.*, pp. 830–840, 2019.

[64] R. Wang, Y. Chen, and W. Lam, “iPFlakies: A framework for detecting and fixing python order-dependent flaky tests,” in *Proc. ACM/IEEE 44th Int. Conf. Softw. Eng.: Companion Proc.*, 2022, pp. 120–124.

[65] P. Branco, S. T. Luís, and R. P. Ribeiro, “A survey of predictive modeling on imbalanced domains,” *ACM Comput. Surveys (CSUR)*, vol. 49, no. 2, pp. 1–50, 2016.

[66] C. Shorten, T. M. Khoshgoftaar, and B. Furht, “Text data augmentation for deep learning,” *J. Big Data*, vol. 8, no. 101, pp. 1–34, 2021.

[67] T. Verdonck, B. Baesens, M. Óskarsdóttir, and S. vanden Broucke, “Special issue on feature engineering editorial,” *Mach. Learn.*, vol. 113, no. 7, pp. 3917–3928, 2021.

[68] R. Pascanu, T. Mikolov, and Y. Bengio, “On the difficulty of training recurrent neural networks,” in *Proc. Int. Conf. Mach. Learn.*, PMLR, 2013, pp. 1310–1318.

[69] R. Collobert et al., “Natural language processing (almost) from scratch,” *J. Mach. Learn. Res.*, vol. 12, no. ARTICLE, pp. 2493–2537, 2011.

[70] J. Micco, “Flaky tests at Google and how we mitigate them,” *Googblogs*, 2016 [Online]. Available: https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html.

[71] F. Thung, D. Lo, and L. Jiang, “Automatic defect categorization,” in *Proc. 19th Work. Conf. Reverse Eng.*, Piscataway, NJ, USA: IEEE Press, 2012, pp. 205–214.

[72] M. Raymond and R. François, “An exact test for population differentiation,” *Evolution*, vol. 49, no. 6, pp. 1280–1283, 1995.

[73] K. Papineni, S. Roukos, T. Ward, and W.-J. Zhu, “BLEU: A method for automatic evaluation of machine translation,” in *Proc. 40th Annu. Meeting Assoc. Comput. Linguistics*, 2002, pp. 1–7.

[74] M. M. Abdollahpour, M. Ashtiani, and F. Bakhshi, “Automatic software code repair using deep learning techniques,” *Softw. Quality J.*, vol. 32, no. 2, pp. 1–30, 2023.

[75] C. Liu et al., “Improving chatGPT prompt for code generation,” 2023, arXiv:2305.08360.

[76] E. Mashhadi and H. Hemmati, “Applying codeBERT for automated program repair of Java simple bugs,” in *Proc. IEEE/ACM 18th Int. Conf. Mining Softw. Repositories (MSR)*, Piscataway, NJ, USA: IEEE Press, 2021, pp. 505–509.

[77] S. Ren et al., “CodeBLEU: A method for automatic evaluation of code synthesis,” 2020, arXiv:2009.10297.

[78] C. Z. Mooney, R. D. Duval, and R. Duvall, *Bootstrapping: A Non-parametric Approach to Statistical Inference*. New York, USA: Sage Publications, no. 95, 1993.

[79] D. W. Hosmer, Jr, S. Lemeshow, and R. X. Sturdivant, *Applied Logistic Regression*. Hoboken, NJ, USA: Wiley, 2013.

[80] E. S. Ristad and P. N. Yianilos, “Learning string-edit distance,” *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 20, no. 5, pp. 522–532, May 1998.

[81] R. F. Woolson, “Wilcoxon signed-rank test,” in *Wiley Encyclopedia of Clinical Trials*, Hoboken, NJ, USA: Wiley, 2007, pp. 1–3.

[82] M. L. McHugh, “The chi-square test of independence,” *Biochemia Medica*, vol. 23, no. 2, pp. 143–149, 2013.

[83] S. F. Assmann, D. W. Hosmer, S. Lemeshow, and K. A. Mundt, “Confidence intervals for measures of interaction,” *Epidemiol.*, vol. 7, no. 3, pp. 286–290, 1996.

[84] M. Evtikhiev, E. Bogomolov, Y. Sokolov, and T. Bryksin, “Out of the BLEU: How should we assess quality of the code generation models?” *J. Syst. Softw.*, vol. 203, no. 111741, pp. 2–12, 2023.

[85] C. L. Goues, M. Pradel, and A. Roychoudhury, “Automated program repair,” *Commun. ACM*, vol. 62, no. 12, pp. 56–65, 2019.

[86] V. Garousi and B. Küçük, “Smells in software test code: A survey of knowledge in industry and academia,” *J. Syst. Softw.*, vol. 138, pp. 52–81, Apr. 2018.

[87] W. Lam, P. Godefroid, S. Nath, A. Santhiar, and S. Thummalapenta, “Root causing flaky tests in a large-scale industrial setting,” in *Proc. 28th ACM SIGSOFT Int. Symp. Softw. Testing Anal.*, 2019, pp. 101–111.

[88] M. Gruber and G. Fraser, “A survey on how test flakiness affects developers and what support they need to address it,” in *Proc. IEEE Conf. Softw. Testing, Verification Validation (ICST)*, Piscataway, NJ, USA: IEEE Press, 2022, pp. 82–92.

[89] N. Nguyen and S. Nadi, “An empirical evaluation of GitHub Copilot’s code suggestions,” in *Proc. 19th Int. Conf. Mining Softw. Repositories*, 2022, pp. 1–5.

[90] F. Ribeiro, N. C. d. M. José, K. Tsushima, R. Abreu, and J. S. João, “GPT-3-powered type error debugging: Investigating the use of large language models for code repair,” in *Proc. 16th ACM SIGPLAN Int. Conf. Softw. Lang. Eng.*, 2023, pp. 2–11.

[91] J. A. Prenner, H. Babii, and R. Robbes, “Can openAI’s codex fix bugs? An evaluation on quixbugs,” in *Proc. 3rd Int. Workshop Automated Program Repair*, 2022, pp. 69–75.

[92] C. S. Xia, Y. Wei, and L. Zhang, “Automated program repair in the era of large pre-trained language models,” in *Proc. 45th Int. Conf. Softw. Eng. (ICSE)*, New York, NY, USA: ACM, 2023, pp. 3–9.

[93] C. S. Xia and L. Zhang, “Less training, more repairing please: Revisiting automated program repair via zero-shot learning,” in *Proc. 30th ACM Joint Eur. Softw. Eng. Conf. Symp. Found. Softw. Eng.*, 2022, pp. 959–971.

---

## TIỂU SỬ TÁC GIẢ (AUTHOR BIOGRAPHIES)

**Sakina Fatima** nhận bằng Thạc sĩ Liên kết Erasmus Mundus chuyên ngành Các Hệ thống Phần mềm Đáng tin cậy (Dependable Software Systems) từ Đại học St. Andrews (Vương quốc Anh) và Đại học Maynooth (Ireland). Cô hiện đang là nghiên cứu sinh Tiến sĩ tại Khoa Kỹ thuật Điện và Khoa học Máy tính, Đại học Ottawa (Canada). Cô là thành viên của Nanda Lab. Cô đã và đang hợp tác nghiên cứu với Microsoft Research, IBM và Huawei. Các hướng nghiên cứu chính của cô bao gồm: kiểm thử phần mềm tự động, AI tạo sinh (generative AI), các mô hình ngôn ngữ lớn (LLMs), và học máy ứng dụng. Năm 2019, cô được trao tặng Huy chương của Chính phủ Pháp và Giải thưởng của Đại học Quốc gia Ireland dành cho thành tích xuất sắc trong các chương trình văn bằng liên kết hợp tác quốc tế.

**Hadi Hemmati** nhận bằng Tiến sĩ từ Đại học Oslo (Na Uy). Ông hiện là Phó Giáo sư tại Khoa Kỹ thuật Điện và Khoa học Máy tính, Đại học York (Canada). Trước đây, ông là Phó Giáo sư tại Khoa Kỹ thuật Điện và Kỹ thuật Phần mềm, Đại học Calgary (AB, Canada). Trong quá khứ, ông cũng từng là Trợ lý Giáo sư tại Đại học Manitoba, và là Nghiên cứu viên sau Tiến sĩ tại Đại học Waterloo và Đại học Queen's. Hướng nghiên cứu chính của ông là kỹ nghệ phần mềm tự động (tập trung vào kiểm thử phần mềm, gỡ lỗi và sửa lỗi tự động), và AI đáng tin cậy (Trustworthy AI - tập trung vào tính mạnh mẽ và khả năng giải thích được). Nghiên cứu của ông đặc biệt chú trọng vào các giải pháp phần mềm/học máy mang tính thực dụng cao cho các hệ thống quy mô công nghiệp lớn và điều tra thực nghiệm chúng trong thực tế. Ông là chủ nhiệm đề tài (PI) của nhiều dự án nghiên cứu công nghiệp trong các lĩnh vực đa dạng như CNTT, hàng không, bảo hiểm, phát triển đô thị, công nghệ tài chính (fintech) và nhiều lĩnh vực khác.

**Lionel C. Briand** (Hội viên Cấp cao IEEE - IEEE Fellow) là Giáo sư kỹ nghệ phần mềm với các vị trí công tác chung tại: (1) Đại học Ottawa (Canada), và (2) Trung tâm Nghiên cứu Phần mềm Quốc gia Ireland Lero SFI - đặt tại Đại học Limerick (Ireland). Với hơn 30 năm hợp tác nghiên cứu cùng các đồng nghiệp, ông đã chủ trì nhiều dự án nghiên cứu công nghiệp với các tập đoàn trong các lĩnh vực ô tô, vệ tinh, hàng không vũ trụ, năng lượng, tài chính và pháp lý. Ông đã đảm nhiệm nhiều chức vụ kỹ thuật, học thuật và lãnh đạo cấp cao tại bảy quốc gia khác nhau. Ông hiện đang giữ vị trí Ghế Nghiên cứu Canada (Canada Research Chair - Tier 1) về "Độ tin cậy và Tính tuân thủ của Phần mềm Thông minh" (Intelligent Software Dependability and Compliance) và là Giám đốc của Lero - Trung tâm Nghiên cứu Phần mềm Quốc gia Ireland. Ông được vinh danh là ACM Fellow cho những đóng góp kiệt xuất trong lĩnh vực kiểm thử và xác minh phần mềm. Ngoài ra, ông còn được trao tặng Giải thưởng Harlan Mills của IEEE Computer Society, Giải thưởng Nghiên cứu Xuất sắc của ACM SIGSOFT, và Giải thưởng Kỹ sư của Năm từ IEEE Reliability Society. Ông cũng được nhận Tài trợ Nghiên cứu Nâng cao của Hội đồng Nghiên cứu Châu Âu (ERC Advanced Grant) năm 2016 về mô hình hóa và kiểm thử các hệ thống không gian-mạng-vật lý (cyber-physical systems)—giải thưởng nghiên cứu cá nhân danh giá nhất của Liên minh Châu Âu—và được bầu làm Viện sĩ Viện Hàn lâm Khoa học thuộc Hội Hoàng gia Canada (Royal Society of Canada) vào năm 2023. Để biết thêm thông tin chi tiết, xem tại: http://www.lbriand.info.
