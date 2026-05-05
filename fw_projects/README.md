# Firmware Projects

Concrete STM32 BIST firmware projects live here using the product/test convention:

```text
fw_projects/<PRODUCT_ID>/<TEST_ID>/
```

Example:

```text
fw_projects/STM32G474VETX/ADC_SINGLE_AC_BIST/
```

Keep the real STM32 toolchain project under the test folder's `project/` subfolder. For new firmware work, create or import this project from STM32CubeMX/STM32CubeIDE first, using MCU/Product Selector, Board Selector, or an approved `.ioc`/template, then let the agent continue the BIST workflow. On Windows, `STM32CubeMX.exe -i` can be used to open STM32CubeMX when `STM32CubeMX.exe` is installed in `PATH`.

Keep reusable BIST behavior as lightweight pattern documents at the repository root, for example [`../ADC_DYNAMIC_SOFTBIST_PATTERN.md`](../ADC_DYNAMIC_SOFTBIST_PATTERN.md). Do not store bulky reference projects here unless they are the actual target firmware project for a specific product/test.

See [`../FW_PROJECT_ARCHITECTURE.md`](../FW_PROJECT_ARCHITECTURE.md) for the full layout and metadata template.